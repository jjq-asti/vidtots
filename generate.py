import subprocess
import sys
import os
import re

ASPECT_RATIO = {
    "1.33" : "4:3",
    "1.77" : "16:9"
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
    proc = subprocess.run(['tovid','id',vid_name],stdout=subprocess.PIPE);
    shell_output = proc.stdout.decode()
    vid_ids = re.findall('\w+ *\w+: \w+\.*\w*\d*', shell_output)
    for id in vid_ids:
        id = id.split(':')
        data[id[0]] = id[1].replace(' ','')
    print(data)
    return data

def generateAVI(vid_ids,vid_resolution,vid_framerate): #AVI is well supported by ffmpeg
     print("Generating AVI...\n\n")
    file_descriptors = {}
    file_descriptors["resolution"] = vid_resolution  #'{}x{}'.format(vid_ids['Width'],vid_ids['Height']) '352x288'
    file_descriptors["frameRate"] = vid_framerate
    file_descriptors["videoBitRate"] = vid_ids['Video bitrate']
    file_descriptors["aspectRatio"] = ASPECT_RATIO[vid_ids['Aspect ratio']]
    file_descriptors["audioBitRate"] = vid_ids['Bitrate']
    file_descriptors["audioSamplingRate"] = vid_ids['Sampling rate']
    file_descriptors["file_name"] =  os.path.splitext( vid_ids['File'])[0] + "_video" + ".avi" 
    vid_name = vid_ids['File']
    command = 'ffmpeg -i {} -b:v {} -r {} -s {} -aspect {} -b:a 48000 {}'.format(vid_name, file_descriptors["videoBitRate"], file_descriptors["frameRate"],
    file_descriptors["resolution"], file_descriptors["aspectRatio"], file_descriptors["file_name"])
    proc = subprocess.run([command], shell=True, stdout=subprocess.PIPE)
    print(file_descriptors)
    return file_descriptors

def generateMPEG2(aviFileDescriptor):
    bit_rate = int(aviFileDescriptor["videoBitRate"])
    max_rate = aviFileDescriptor["videoBitRate"]
    min_rate = aviFileDescriptor["videoBitRate"]
    mpeg2_filename = os.path.splitext(aviFileDescriptor["file_name"])[0] + ".mp2" 
    if os.path.exists(mpeg2_filename):
        subprocess.run(['rm', 'mpeg2_filename'])
    command = "ffmpeg -i {} -an -vcodec mpeg2video -f mpeg2video -b:v {} -maxrate {} -minrate {} -bf 2 \
        -bufsize 1835008 {}".format(aviFileDescriptor["file_name"],bit_rate,max_rate,min_rate, mpeg2_filename)
    proc = subprocess.run(command,shell=True, stdout=subprocess.PIPE)
    return proc

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

def generateVideoPES():
    pes_filename = os.path.splitext(aviFileDescriptor["file_name"])[0] + ".pes"
    command = "esvideompeg2pes {} > {}".format(aviFileDescriptor["file_name"],pes_filename)
    proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    return proc

def generateVideoTS(aviFileDescriptor):
    vid_bit_rate = int(aviFileDescriptor["videoBitRate"]) * (1 + 0.15)
    command = "pesvideo2ts 2064 25 112 {} 0 {} > sample_video.ts".format(
    vid_bit_rate, "sample_video.pes")
    proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE)

def getAudioFrameSize(audioFileName):
    audioDescriptor = {}
    command = "esaudioinfo sample.avi"
    proc = subprocess.run(command, shell=True, stdout = subprocess.PIPE)
    shell_output = proc.stdout.decode()
    all_test = shell_output.split("\n\n")
    final_result = all_test.pop()
    print(final_result)
    values = re.findall("\d{2,}",final_result)
    print(values)
    audioDescriptor["frame_size"] = values[1]
    audioDescriptor["sampling_rate"] = values[0]
    return audioDescriptor

def extractAudioToMp2(aviFileDescriptor):
    print("extracting audio....: {}".format(aviFileDescriptor["audioSamplingRate"]))
    command = "ffmpeg -i sample.avi -vn -ac 2 -acodec mp2 -f mp2 -b:a 383000 -ar 48000 sample_audio.mp2"
    subprocess.run(command, shell = True, stdout = subprocess.PIPE)

def generateAudioPES(aviFileDescriptor,audioDescriptor):
    command = "esaudio2pes sample_audio.mp2 1152 {} {} -1 3600 > sample_audio.pes".format(aviFileDescriptor["audioSamplingRate"],
    audioDescriptor["frame_size"])

def generateAudioTS(aviFileDescriptor,audioDescriptor):
    command = "pesaudio2ts 2068 1152 {} {} 0 sample_audio.pes > sample_audio.ts".format(aviFileDescriptor["audioSamplingRate"],
    audioDescriptor["frame_size"])
    subprocess.run(command, shell = True, stdout = subprocess.PIPE)

def muxTS():
    command = "tscbmuxer b:{} sample.ts b:{} "
if __name__ == "__main__":
    vidFile = sys.argv[1]
    vidResolution = sys.argv[2]
    vidFramerate = sys.argv[3]
    vidAspectRatio = sys.argv[4]
    vid_ids = getVideoID(vidFile)
    aviFileDescriptor = generateAVI(vid_ids,vidResolution,vidFramerate)
    mp2FileName = generateMPEG2(aviFileDescriptor)
    generateVideoPES()
    generateVideoTS(aviFileDescriptor)


    audioDescriptor = getAudioFrameSize(vidFile)
    extractAudioToMp2(aviFileDescriptor)
    generateAudioPES(aviFileDescriptor, audioDescriptor)
    generateAudioTS(aviFileDescriptor, audioDescriptor)




