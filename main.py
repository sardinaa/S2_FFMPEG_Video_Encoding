import subprocess
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import json
import numpy as np


class FFMpeg:
    def __init__(self, variables):
        self.name = variables["name"]
        self.name_2 = variables["name_2"]
        self.start_cutting = variables["start"]
        self.finish_cutting = variables["finish"]

    def macroblocks_motion_v(self):
        subprocess.getstatusoutput("ffmpeg -flags2 +export_mvs -i "
                                   "" + self.name + ""
                                                    " -vf codecview=mv=pf+bf"
                                                    "+bb output.mp4")

    def container(self):
        ffmpeg_extract_subclip(self.name_2, self.start_cutting,
                               self.finish_cutting, targetname="test.mp4")
        # https://stackoverflow.com/questions/28495514/how-to-extract-audio-from-mpeg-4-file-using-ffmpeg
        subprocess.getstatusoutput("ffmpeg -i test.mp4 -vn -ac 2 -ar 44100 "
                                   "-ab 320k -f mp3 output.mp3")
        # https://trac.ffmpeg.org/wiki/Encode/AAC
        subprocess.getstatusoutput("ffmpeg -i test.mp4 -c:a aac -b:a 64k "
                                   "output.aac")
        # https://stackoverflow.com/questions/11779490/how-to-add-a-new-audio-not-mixing-into-a-video-using-ffmpeg
        # https://medium.com/av-transcode/how-to-add-multiple-audio-tracks-to-a-single-video-using-ffmpeg-open-source-tool-27bff8cca30
        subprocess.getstatusoutput("ffmpeg -i test.mp4 -i output.mp3 -i "
                                   "output.aac -map 0:v -map 1:a -map 2:a "
                                   "-codec copy -shortest container.mp4")

    def read_container(self):
        # https://stackoverflow.com/questions/11400248/using-ffmpeg-to-get-video-info-why-do-i-need-to-specify-an-output-file
        subprocess.getstatusoutput("ffprobe -v quiet -print_format json "
                                   "-show_format -show_streams container.mp4 "
                                   "> container.mp4.json")

        # Input the key value that you want to search
        keyVal = 'codec_name'
        acces = "streams"
        file = open("container.mp4.json", )
        # load the json data
        data = json.load(file)
        # Search the key value using 'in' operator
        codec_video = []
        codec_audio = []
        codecs = {
            "video": ["mpeg2", "h264", "avs", "avs+"],
            "audio": ["aac", "mp3", "h264", "ac3"]
        }

        broadcasting = {
            "DVB": {
                "video": ["mpeg2", "h264"],
                "audio": ["aac", "ac3", "mp3"]
            },
            "ISDB": {
                "video": ["mpeg2", "h264"],
                "audio": ["aac"]
            },
            "ATSC": {
                "video": ["mpeg2", "h264"],
                "audio": ["ac3"]
            },
            "DTMB": {
                "video": ["mpeg2", "h264", "avs", "avs+"],
                "audio": ["aac", "ac3", "mp3", "mp2", "dra"]
            }
        }

        for i in range(len(data[acces])):
            if keyVal in data[acces][i]:
                if data[acces][i][keyVal] in codecs["video"]:
                    codec_video.append(data[acces][i][keyVal])
                    print("The video codec on this container is",
                          data[acces][i][keyVal])
                else:
                    print("The audio codec on this container is",
                          data[acces][i][keyVal])
                    codec_audio.append(data[acces][i][keyVal])

            else:
                # Print the message if the value does not exist
                print("%s is not found in JSON data" % keyVal)

        count = 0
        if set(codec_video).issubset(broadcasting["DVB"]["video"]) and \
                set(codec_audio).issubset(broadcasting["DVB"]["audio"]):
            count += 1
            print("The codecs of this container fits well with DVB "
                  "broadcasting standard")
        if set(codec_video).issubset(broadcasting["DTMB"]["video"]) and \
                set(codec_audio).issubset(broadcasting["DTMB"]["audio"]):
            count +=1
            print("The codecs of this container fits well with DTMB "
                  "broadcasting standard")
        if set(codec_video).issubset(broadcasting["ATSC"]["video"]) and \
                set(codec_audio).issubset(broadcasting["ATSC"]["audio"]):
            count += 1
            print("The codecs of this container fits well with ATSC "
                  "broadcasting standard")
        if set(codec_video).issubset(broadcasting["ISDB"]["video"]) and \
                set(codec_audio).issubset(broadcasting["ISDB"]["audio"]):
            count += 1
            print("The codecs of this container fits well with ISDBS "
                  "broadcasting standard")
        if count == 0:
            print("No broadcasting standard is compatible with the codecs of "
                  "this container")

    def subtitles(self):
        subprocess.getstatusoutput("curl -o subtitles.eng.srt "
                                   "https://raw.githubusercontent.com/moust"
                                   "/MediaPlayer/master/demo/subtitles.srt")
        subprocess.getstatusoutput("ffmpeg -i container.mp4 -vf "
                                   "subtitles=subtitles.eng.srt "
                                   "mysubtitledmovie.mp4")
        subprocess.getstatusoutput("ffplay mysubtitledmovie.mp4")



    def clean(self):
        subprocess.getstatusoutput("unlink output.mp4")
        subprocess.getstatusoutput("unlink test.mp4")
        subprocess.getstatusoutput("unlink output.mp3")
        subprocess.getstatusoutput("unlink output.aac")
        subprocess.getstatusoutput("unlink container.mp4")
        subprocess.getstatusoutput("unlink mysubtitledmovie.mp4")
        subprocess.getstatusoutput("unlink container.mp4.json")
        subprocess.getstatusoutput("unlink subtitles.eng.srt")


if __name__ == '__main__':
    variables = {
        "name": "BBB_cutted.mp4",
        "name_2": "BBB.mp4", #complete video of big buck bunny
        "start": 0,
        "finish": 60
    }
    ff = FFMpeg(variables)
    #ff.clean() Uncomment only to delete the files generated
    ff.macroblocks_motion_v()
    ff.container()
    ff.read_container()
    ff.subtitles()
