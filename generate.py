import subprocess
import sys
import os
import re
import json
import xmltodict

vidFile = ""

ASPECT_RATIO = {
    "1.33" : "4:3",
    "1.77" : "16:9",
    "1.778" : "16:9",
}


DVB_SIGNALING = {
    "PAT": 3008,
    "PMT": 3008,
    "SDT": 1500,
    "NIT": 1400,
    "AIT": 2000 #used by data carousel
}

def getVideoID(vid_name):
    print("Getting Video ID...\n\n")
    data = {}
    proc = subprocess.run("mediainfo --Output=XML " + vid_name, shell=True, stdout=subprocess.PIPE);
    xml = proc.stdout
    my_dict_string = xmltodict.parse(xml)
    my_dict =  json.dumps(my_dict_string, indent=4, sort_keys=True)
    print(my_dict) 
    my_dict = json.loads(my_dict)
    video_attrib = my_dict['MediaInfo']['media']['track']
    return video_attrib

def generateAVI(vid_ids): #AVI is well supported by ffmpeg
    general = vid_ids[0]
    vid = vid_ids[1]
    aud = vid_ids[2]
    print("Generating AVI...\n\n")
    file_descriptors = {}
    file_descriptors["resolution"] = '{}x{}'.format(vid['Sampled_Width'],vid['Sampled_Height'])
    file_descriptors["frameRate"] = vid['FrameRate']
    file_descriptors["videoBitRate"] = vid['BitRate']
    file_descriptors["aspectRatio"] = ASPECT_RATIO[vid['DisplayAspectRatio']]
    file_descriptors["audioBitRate"] = aud['BitRate']
    file_descriptors["audioSamplingRate"] = aud['SamplingRate']
    file_descriptors["MaxRate"] = general['OverallBitRate']
    file_descriptors["file_name"] =  os.path.splitext( vidFile)[0]  + "_video" + ".avi" 

    command = 'ffmpeg -i {} -b:v {} -r {} -s {} -aspect {} -b:a {} {}'.format(vidFile, file_descriptors["videoBitRate"], file_descriptors["frameRate"],
    file_descriptors["resolution"], file_descriptors["aspectRatio"], file_descriptors['audioBitRate'],file_descriptors["file_name"])
    proc = subprocess.run([command], shell=True, stdout=subprocess.PIPE)
    print(file_descriptors)
    return file_descriptors

def generateMPEG2(aviFileDescriptor):
    bit_rate = int(aviFileDescriptor["videoBitRate"])
    max_rate = aviFileDescriptor["MaxRate"]
    min_rate = aviFileDescriptor["audioBitRate"]
    mpeg2_filename = os.path.splitext(aviFileDescriptor["file_name"])[0] + ".m2v" 
    if os.path.exists(mpeg2_filename):
        subprocess.run(['rm', 'mpeg2_filename'])
    command = "ffmpeg -i {} -an -vcodec mpeg2video -f mpeg2video -s {} -r {} -aspect {} -deinterlace -b:v {} -maxrate {} -minrate {} -bf 2 \
    -bufsize 1835008 {}".format(aviFileDescriptor["file_name"],aviFileDescriptor['resolution'], aviFileDescriptor['frameRate'],aviFileDescriptor['aspectRatio'],  bit_rate,max_rate,min_rate, mpeg2_filename)
    proc = subprocess.run(command,shell=True, stdout=subprocess.PIPE)
    sys.exit(0)
    return mpeg2_filename

# def generateMPEG2Improved(aviFileDescriptor):
#     if os.path.exists('sample_video.mp2'):
#         subprocess.run('rm sample_video.mp2', shell=True)
#     command = "ffmpeg -i {} -an -s {} -deinterlace -r {} -aspect {} -f yuv4mpegpipe - | yuvdenoise | ffmpeg \
#         -i - -an -vcodec mpeg2video -f mpeg2video -b:v {} -maxrate {} -minrate {} -bf 2 -bufsize 1343488 sample_video.mp2".format(
#             aviFileDescriptor["file_name"],aviFileDescriptor["resolution"], aviFileDescriptor["frameRate"], aviFileDescriptor["aspectRatio"],
#             aviFileDescriptor["videoBitRate"],aviFileDescriptor["videoBitRate"],aviFileDescriptor["videoBitRate"]
#         )
#     proc = subprocess.run(command, shell=True, stdout = subprocess.PIPE)
#     return proc

def generateVideoPES(mp2filename):
    mp2_name = mp2filename
    pes_filename = os.path.splitext(mp2_name)[0] + ".pes"
    command = "esvideompeg2pes {} > {}".format(mp2_name,pes_filename)
    proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    return pes_filename

def generateVideoTS(aviFileDescriptor, pes_name):
    ts_filename = os.path.splitext(pes_name)[0] + ".ts" 
    vid_bit_rate = int(aviFileDescriptor["videoBitRate"]) * (1 + 0.15)
    command = "pesvideo2ts 2064 25 112 {} 0 {} > {}".format(
    vid_bit_rate, pes_name, ts_filename)
    proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    return ts_filename

def getAudioFrameSize(audioFileName):
    audioDescriptor = {}
    command = "esaudioinfo " + audioFileName
    proc = subprocess.run(command, shell=True, stdout = subprocess.PIPE)
    shell_output = proc.stdout.decode()
    all_test = shell_output.split("\n\n")
    final_result = all_test.pop()
    values = re.findall("\d{2,}",final_result)
    audioDescriptor["frame_size"] = values[1]
    audioDescriptor["sampling_rate"] = values[0]
    print(audioDescriptor)
    sys.exit(0)
    return audio_framesize

def extractAudioToMp2(aviFileDescriptor):
    avi_name = aviFileDescriptor['file_name']
    audio_avi_name = os.path.splitext(avi_name)[0] + "_audio" + ".mp2"
    audio_sampling_rate = aviFileDescriptor["audioSamplingRate"]
    audio_bitrate = aviFileDescriptor["audioBitRate"] 

    print("extracting audio....: {}".format(audio_sampling_rate))
    command = "ffmpeg -i {} -vn -ac 2 -acodec mp2 -f mp2 -b:a {} -ar {} {}".format(avi_name, audio_bitrate, audio_sampling_rate,audio_avi_name)
    subprocess.run(command, shell = True, stdout = subprocess.PIPE)

def generateAudioPES(aviFileDescriptor,audio_framesize):
    avi_name = aviFileDescriptor['file_name']
    audio_sampling_rate = aviFileDescriptor["audioSamplingRate"]
    audio_pes_name = os.path.splitext(avi_name)[0] + "_audio" + ".pes"
    audio_mp2 = os.path.splitext(avi_name)[0] + "_audio" + ".mp2"
    command = "esaudio2pes {} {} {} 768 -1 3600 > {}".format(audio_mp2,audio_framesize, aviFileDescriptor["audioSamplingRate"], audio_framesize, audio_pes_name)
    subprocess.run(command, shell = True, stdout = subprocess.PIPE)

def generateAudioTS(aviFileDescriptor, audio_framesize):
    avi_name = aviFileDescriptor['file_name']
    audio_sampling_rate = aviFileDescriptor["audioSamplingRate"]
    audio_bitrate = aviFileDescriptor["audioBitRate"] 
    audio_ts_name = os.path.splitext(avi_name)[0] + "_audio" + ".ts"
    audio_pes_name = os.path.splitext(avi_name)[0] + "_audio" + ".pes"
    command = "pesaudio2ts 2068 {} {} 768 -1 0 {} > {}".format(audio_framesize,aviFileDescriptor["audioSamplingRate"], audio_pes_name,audio_ts_name)
    subprocess.run(command, shell = True, stdout = subprocess.PIPE)

def muxTS():
    command = "tscbmuxer b:{} sample.ts b:{} "
if __name__ == "__main__":
    vidFile = sys.argv[1]
    #vidResolution = sys.argv[2]
    #vidFramerate = sys.argv[3]
    #vidAspectRatio = sys.argv[4]

    vid_ids = getVideoID(vidFile) #working
    aviFileDescriptor = generateAVI(vid_ids) #working
    mp2FileName = generateMPEG2(aviFileDescriptor) #working

    pes_name = generateVideoPES(mp2FileName) 
    ts_name = generateVideoTS(aviFileDescriptor,pes_name)
    audio_framesize = getAudioFrameSize(aviFileDescriptor['file_name'])

    extractAudioToMp2(aviFileDescriptor)
    generateAudioPES(aviFileDescriptor, audio_framesize)
    generateAudioTS(aviFileDescriptor, audio_framesize)




