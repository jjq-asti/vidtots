#!/usr/bin/env python

import subprocess
import sys
import os
import re
import json
import xmltodict

vidFile = ""

ASPECT_RATIO = {
    "1.33" : "4:3",
    "1.333" : "4:3",
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
    my_dict = json.loads(my_dict)
    video_attrib = my_dict['MediaInfo']['media']['track']
    return video_attrib

def generateAVI(vid_ids): #AVI is well supported by ffmpeg
    general = vid_ids[0]
    vid = vid_ids[1]
    aud = vid_ids[2]
    print("Generating AVI...\n\n")

    file_descriptors = {}
    file_descriptors["resolution"]          = '{}x{}'.format(vid['Sampled_Width'],vid['Sampled_Height'])
    file_descriptors["frameRate"]           = vid['FrameRate']
    file_descriptors["videoBitRate"]        = vid['BitRate']
    file_descriptors["aspectRatio"]         = ASPECT_RATIO[vid['DisplayAspectRatio']]
    file_descriptors["audioBitRate"]        = aud['BitRate']
    #file_descriptors['audioMaxBitRate']     = aud['BitRate_Maximum']
    file_descriptors["audioSamplingRate"]   = aud['SamplingRate']
    file_descriptors["MaxRate"]             = general['OverallBitRate']
    file_descriptors["file_name"]           = os.path.splitext( vidFile)[0]  + "_video" + ".avi" 
    fps_initial = int(float(file_descriptors["frameRate"])) 
    if fps_initial < 25:  #NTSC/TV 30fps
        file_descriptors["frameRate"] = 25
    pts = (int(float(file_descriptors["frameRate"])) / fps_initial)
    pts = int(1)
    file_descriptors['pts'] = pts
    tempo =  fps_initial / int(float(file_descriptors["frameRate"]))
    file_descriptors['tempo'] = tempo

    print(file_descriptors)
    # command = 'ffmpeg -i {} -b:v {} -r {} -s {} -aspect {} -b:a {} {}'.format(vidFile, 
    #     file_descriptors["videoBitRate"], file_descriptors["frameRate"], 
    #     file_descriptors["resolution"], file_descriptors["aspectRatio"], 
    #     file_descriptors['audioBitRate'],file_descriptors["file_name"])
    #command = 'ffmpeg -i {} -s 320x240 -aspect 4:3 -r 15 -c:v libx264 -c:a aac -b:a 384k {}'.format(

    command = "ffmpeg -i {} -r {} {}".format(
        vidFile, 
        file_descriptors['frameRate'],
        file_descriptors["file_name"])

    proc = subprocess.run([command], shell=True, stdout=subprocess.PIPE)
    return file_descriptors

def generateMPEG2(aviFileDescriptor):
    bit_rate =  "1000k" #aviFileDescriptor["MaxRate"] + "k"  #int(aviFileDescriptor["videoBitRate"])
    max_rate =  "1000k" #aviFileDescriptor["MaxRate"] + "k"
    min_rate =  "1000k" #aviFileDescriptor["MaxRate"] + "k"  #aviFileDescriptor["audioBitRate"]
    mpeg2_filename = os.path.splitext(aviFileDescriptor["file_name"])[0] + ".m2v"
    print(mpeg2_filename)

   # if os.path.exists(mpeg2_filename):
   #     subprocess.run(['rm', 'mpeg2_filename'], stdout = subprocess.PIPE, stderr = stdout)
   #-r {} -filter:v 'setpts={}*PTS' -filter:a 'atempo=2'
    command = "ffmpeg -i {} -an -s {} -deinterlace -aspect {} " \
              "-filter:v 'setpts={}*PTS' " \
              "-f yuv4mpegpipe - | yuvdenoise | ffmpeg -i - -an -vcodec " \
              "mpeg2video -f mpeg2video -b:v {} -maxrate {} -minrate {} " \
              "-bf 2 -bufsize 1343488 {}".format(
        aviFileDescriptor["file_name"],  
        aviFileDescriptor["resolution"],
        aviFileDescriptor["aspectRatio"],
        aviFileDescriptor["pts"],
        bit_rate, max_rate, 
        min_rate, mpeg2_filename)
        
    proc = subprocess.run(command,shell=True, stdout=subprocess.PIPE)
    return mpeg2_filename

def generateVideoPES(mp2filename):
    mp2_name = mp2filename
    pes_filename = os.path.splitext(mp2_name)[0] + ".pes"

    command = "esvideompeg2pes {} > {}".format(mp2_name,pes_filename)
    proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE)

    return pes_filename

def generateVideoTS(aviFileDescriptor, pes_name): 
    ts_filename = os.path.splitext(pes_name)[0] + ".ts" 
    vid_bit_rate = 1000000 * (1 + 0.15)
   
    command = "pesvideo2ts 2065 {} 112 {} 0 {} > {}".format(
    aviFileDescriptor['frameRate'],
    vid_bit_rate, 
    pes_name, 
    ts_filename )

    proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE)

    return ts_filename

def extractAudioToMp2(aviFileDescriptor):
    avi_name = aviFileDescriptor['file_name']
    audio_mp2_name = os.path.splitext(vidFile)[0] + "_audio" + ".mp2"
    audio_sampling_rate = aviFileDescriptor["audioSamplingRate"]
    audio_bitrate = 128000 #aviFileDescriptor["audioBitRate"] 
    temp = 1

    print(audio_sampling_rate, audio_bitrate)

    print("extracting audio....: {}".format(audio_sampling_rate))
    command = "ffmpeg -i {} -vn -ac 2 -acodec mp2 -f mp2 -filter:a 'atempo={}' -b:a {} -ar {} {}".format(
        avi_name,
        temp,
        audio_bitrate, 
        audio_sampling_rate, 
        audio_mp2_name )
        
    subprocess.run(command, shell = True, stdout = subprocess.PIPE)
    return audio_mp2_name


def getAudioFrameSize(audioFileName):
    audioDescriptor = {}
    command = "esaudioinfo " + audioFileName
    proc = subprocess.run(command, shell=True, stdout = subprocess.PIPE)
    shell_output = proc.stdout.decode()
    all_test = shell_output.split("\n\n")
    all_test.pop()
    final_result = all_test.pop()
    x,y = re.search("\d+Hz", final_result).span()
    audioDescriptor["sampling_rate"] = final_result[x:y-2]
    x,y = re.search("\d+\sbytes", final_result).span()
    audioDescriptor["frame_size"] = final_result[x:y-6]
    print(audioDescriptor)
    return audioDescriptor

def generateAudioPES(audio_mp2_name, audioDescriptor):
    audio_framesize = audioDescriptor['frame_size']
    audio_sampling_rate = audioDescriptor['sampling_rate'] 
    audio_pes_name = os.path.splitext(vidFile)[0] + "_audio" + ".pes"

    command = "esaudio2pes {} {} {} 384 -1 3600 > {}".format(
        audio_mp2_name,
        audio_sampling_rate,
        audio_framesize,
        audio_pes_name )

    subprocess.run(command, shell = True, stdout = subprocess.PIPE)
    return audio_pes_name

def generateAudioTS(audio_pes_name, audioDescriptor):
    audio_sampling_rate = audioDescriptor['sampling_rate'] 
    audio_ts_name = os.path.splitext(vidFile)[0] + "_audio" + ".ts"

    command = "pesaudio2ts 2075 1152 {} {} 0 {} > {}".format(
        audio_sampling_rate, 
        audioDescriptor['frame_size'],
        audio_pes_name,
        audio_ts_name )

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
    

    audio_mp2_name = extractAudioToMp2(aviFileDescriptor)
    audioDescriptor = getAudioFrameSize(audio_mp2_name)

    audio_pes_name = generateAudioPES(audio_mp2_name, audioDescriptor)
    print("generate audio ts")
    generateAudioTS(audio_pes_name, audioDescriptor)




