#!/bin/bash
echo "IMAGE_F1C2CH0 ORIENTACION N45O"
#python RTDI_OUT_HF.py -path /home/hfuser1204/HFA -f 3.64 -code 2 -lo 31 -ch 0#modo campaign
python RTDI_OUT_HF.py -path /home/hfuser/HFB -C 0 -ii 6 -f 3.64990234375 -code 2 -lo 12 -ch 0 #mode normal

echo "IMAGE_F1C2CH1 ORIENTACION N45E"
#python RTDI_OUT_HF.py -path /home/hfuser1204/HFA -f 3.64 -code 2 -lo 32 -ch 1#modo campaign
python RTDI_OUT_HF.py -path /home/hfuser/HFB -C 0 -ii 6 -f 3.64990234375 -code 2 -lo 12 -ch 1 #mode normal

