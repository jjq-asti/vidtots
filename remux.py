#!/usr/bin/env python

import sys
import subprocess
import time

reception_1_layer_bit_rate = 19329000

def sum_bit_rates(*args):
    return sum(args)

def generate_tables():
    subprocess.run(["python", "gtables.py"])

def update_ocidr(ocdir):
    ocupdate = "oc-update.sh {} 0x0C 1 2004 2".format(ocdir)
    subprocess.run(ocupdate, shell=True,stdout=subprocess.PIPE)

def mux_ts(vid_ts, vid_bitrate, aud_ts, aud_bitrate, ocdir_bitrate, ocdir_ts ):
    pat = 15040
    pmt_sd = 15040
    sdt = 3008
    nit = 3008
    ait = 3008
    vid = 1136000
    aud = 188000

    ts_bit_rate = sum_bit_rates(pat, pmt_sd, sdt, nit, ait, ocdir_bitrate, vid_bitrate, aud_bitrate)

    if ts_bit_rate > reception_1_layer_bit_rate:
        raise ValueError("Bit Rate too large")
    elif ts_bit_rate < reception_1_layer_bit_rate:
        null = reception_1_layer_bit_rate - ts_bit_rate
    else:
        null = 0

    print("total bitrate: {}".format(null + ts_bit_rate)) 
    print("null bitrate: {}\n".format(null))

    remux = "tscbrmuxer b:{} pat.ts b:{} pmt_sd.ts b:{} sdt.ts " \
            "b:{} nit.ts b:{} ait.ts b:{} {} c:{} {} " \
            "b:{} {} b:{} null.ts > /tmp/videofinal1.ts".format(pat, pmt_sd, sdt, nit,
                    ait,   ocdir_bitrate, ocdir_ts,  vid_bitrate, vid_ts, aud_bitrate, aud_ts, null)

    subprocess.run(remux, shell=True,stdout=subprocess.PIPE)

def stamp_ts():
    stamp = "tsstamp /tmp/videofinal1.ts {} > /tmp/channel_program.ts".format(
        reception_1_layer_bit_rate)
    subprocess.run(stamp, shell=True,stdout=subprocess.PIPE)

def demux():
    mount_point = '/media/demux'
    umount = 'umount'
    mount  = 'mount'

    demuxfs = "demuxfs -o backend=filesrc -o filesrc=/tmp/channel_program.ts {}".format(mount_point)
    subprocess.run([umount, mount_point])
    subprocess.run(demuxfs, shell=True)

if __name__ == "__main__":
    # output_name = sys.argv[1]

    video_ts_name = sys.argv[1]
    audio_ts_name = sys.argv[2]
    video_ts_bitrate = 5e6 * 1.15 #sys.argv[2]
    audio_ts_bitrate = 188000     #sys.argv[2]
    ocdir_rate = int(sys.argv[3])
    ocdir = sys.argv[4]
    ocdir_ts = ocdir + ".ts"
    print(ocdir_ts)
    
    generate_tables()
    update_ocidr(ocdir)
    mux_ts(video_ts_name, video_ts_bitrate, audio_ts_name, audio_ts_bitrate, ocdir_rate, ocdir_ts)
    stamp_ts()





    #subprocess.run(gtable, shell=True,stdout=subprocess.PIPE)

    # subprocess.run([mount, mount_point])
