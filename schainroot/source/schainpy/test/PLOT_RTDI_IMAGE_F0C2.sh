#!/bin/bash
echo "IMAGE_F0C2CH0 ORIENTACION N45O"
#python RTDI_OUT_HF.py -path /home/hfuser1204/HFA -f 2.72 -code 2 -lo 31 -ch 0# modo campaign
python RTDI_OUT_HF.py -path /home/hfuser1204/HFA -C 0 -ii 6 -f 2.72 -code 2 -lo 31 -ch 0 # modo normal
echo "IMAGE_F0C2CH1 ORIENTACION N45E"
#python RTDI_OUT_HF.py -path /home/hfuser1204/HFA -f 2.72 -code 2 -lo 32 -ch 1#modo campaign
python RTDI_OUT_HF.py -path /home/hfuser1204/HFA -C 0 -ii 6 -f 2.72 -code 2 -lo 32 -ch 1 #modo normal
