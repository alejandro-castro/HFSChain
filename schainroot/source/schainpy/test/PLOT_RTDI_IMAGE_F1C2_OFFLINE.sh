#!/bin/bash
echo "IMAGE_F1C2CH0 ORIENTACION N45O"
#python RTDI_OUT_HF.py -path /home/hfuser/HFA -f 3.64 -code 2 -lo 31 -ch 0 -date "2018/02/07" # modo campaña
#python RTDI_OUT_HF.py -path /home/hfuser/HFA -C 0 -ii 6 -f 3.64990234375 -code 2 -lo 11 -ch 0  -date "2018/04/15" #mode normal
python RTDI_OUT_HF.py -path /home/hfuser/HFB -C 0 -ii 6 -f 3.64990234375  -code 2 -lo 12 -ch 0  -date "2018/06/22" #mode normal
echo "IMAGE_F1C2CH1 ORIENTACION N45E"
#python RTDI_OUT_HF.py -path /home/hfuser/HFA -f 3.64 -code 2 -lo 32 -ch 1 -date "2018/02/07" # modo campaña
#python RTDI_OUT_HF.py -path /home/hfuser/HFA -C 0 -ii 6 -f 3.64990234375  -code 2 -lo 11 -ch 1  -date "2018/04/15" #mode normal
python RTDI_OUT_HF.py -path /home/hfuser/HFB -C 0 -ii 6 -f 3.64990234375  -code 2 -lo 12 -ch 1  -date "2018/06/22" #mode normal

