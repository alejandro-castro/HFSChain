#!/bin/bash
echo "IMAGE_F0C0CH0 ORIENTACION N450"   
#python RTDI_OUT_HF.py -path /home/hfuser1204/HFA -f 2.72 -code 0 -lo 31 -ch 0# modo campaign
python RTDI_OUT_HF.py -path /home/hfuser/HFA -C 0 -ii 6 -f 2.72216796875 -code 0 -lo 11 -ch 0 # modo normal
echo "IMAGE_F0C0CH1 ORIENTACION N45O"
#python RTDI_OUT_HF.py -path /home/hfuser1204/HFA -f 2.72 -code 0 -lo 32 -ch 1#modocampaign
python RTDI_OUT_HF.py -path /home/hfuser/HFA -C 0 -ii 6 -f 2.72216796875 -code 0 -lo 11 -ch 1 # modo normal
