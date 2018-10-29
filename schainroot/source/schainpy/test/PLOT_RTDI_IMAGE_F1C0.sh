#!/bin/bash
echo "IMAGE_F1C0CH0 ORIENTACION N45O"
#python RTDI_OUT_HF.py -path /home/hfuser1204/HFA -f 3.64 -code 0 -lo 31 -ch 0#modo campaign
python RTDI_OUT_HF.py -path /home/hfuser1204/HFA -C 0 -ii 6 -f 3.64 -code 0 -lo 31 -ch 0 # modo normal
echo "IMAGE_F1C0CH1 ORIENTACION N45E"
#python RTDI_OUT_HF.py -path /home/hfuser1204/HFA -f 3.64 -code 0 -lo 32 -ch 1 #modo campaign
python RTDI_OUT_HF.py -path /home/hfuser1204/HFA -C 0 -ii 6 -f 3.64 -code 0 -lo 32 -ch 1 #modo normal 
