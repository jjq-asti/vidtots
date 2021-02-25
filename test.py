#!/usr/bin/env python

import sys
import subprocess
import time

def sum_bit_rates(*args):
    return sum(args)


if __name__ == "__main__":
    # output_name = sys.argv[1]
    vid_name = sys.argv[1]
    aud_name = sys.argv[2]
    ocdir = 2000000 #int(sys.argv[3])
    print(vid_name, aud_name, ocdir)
    reception_1_layer_bit_rate = 19329000
    pat = 15040
    pmt_sd = 15040
    sdt = 3008
    nit = 3008
    ait = 3008
    vid = 1136000
    aud = 188000
    
    ts_bit_rate = sum_bit_rates(pat, pmt_sd, sdt, nit, ait, ocdir, vid, aud)
    if ts_bit_rate > reception_1_layer_bit_rate:
        raise ValueError("Bit Rate too large")
    elif ts_bit_rate < reception_1_layer_bit_rate:
        null = reception_1_layer_bit_rate - ts_bit_rate
    else:
        null = 0

    print("total bitrate: {}".format(null + ts_bit_rate)) 
    print("null bitrate: {}\n".format(null))

    gtable = "./gtables.py"
    ocupdate = "oc-update.sh ocdir1 0x0C 1 2004 2"

    remux = "tscbrmuxer b:{} pat.ts b:{} pmt_sd.ts b:{} sdt.ts " \
            "b:{} nit.ts b:{} ait.ts b:{} ocdir1.ts c:{} {} " \
            "b:{} {} b:{} null.ts > /tmp/videofinal1.ts".format(pat, pmt_sd, sdt, nit,
                    ait,   ocdir, vid, vid_name, aud, aud_name, null)

    stamp = "tsstamp /tmp/videofinal1.ts {} > /tmp/channel_program.ts".format(
        reception_1_layer_bit_rate)

    mount_point = '/media/demux'
    umount = 'umount'
    mount  = 'mount'

    demuxfs = "demuxfs -o backend=filesrc -o filesrc=/tmp/channel_program.ts {}".format(mount_point)

    subprocess.run(gtable, shell=True,stdout=subprocess.PIPE)
    subprocess.run(ocupdate, shell=True,stdout=subprocess.PIPE)
    subprocess.run(remux, shell=True,stdout=subprocess.PIPE)
    subprocess.run(stamp, shell=True,stdout=subprocess.PIPE)

    subprocess.run([umount, mount_point])
    subprocess.run(demuxfs, shell=True)
    # subprocess.run([mount, mount_point])
