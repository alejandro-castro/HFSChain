#!/bin/bash
echo "IMAGE_F0C0CH0 ORIENTACION N450"   

#python RTDI_OUT_HF.py -path /home/hfuser/HFA -f 2.72216796875 -code 0 -lo 11 -ch 0 -date "2018/02/07" # modo campaña
#python RTDI_OUT_HF.py -path /home/hfuser/HFB -f 2.72216796875 -code 0 -lo 12 -ch 0 -date "2018/02/07" # modo campaña

################### MODO NORMAL #################
#################################################
#python RTDI_OUT_HF.py -path /home/hfuser/HFA -C 0 -ii 6 -f 2.72216796875 -code 0 -lo 11 -ch 0 -date "2018/04/15" # modo normal
python RTDI_OUT_HF.py -path /home/hfuser/HFB -C 0 -ii 6 -f 2.72216796875 -code 0 -lo 12 -ch 0 -date "2018/06/22" # modo normal


echo "IMAGE_F0C0CH1 ORIENTACION N45E"

#python RTDI_OUT_HF.py -path /home/hfuser/HFA -f 2.72216796875 -code 0 -lo 11 -ch 1 -date "2018/02/07" # modo campaña
#python RTDI_OUT_HF.py -path /home/hfuser/HFB -f 2.72216796875 -code 0 -lo 12 -ch 1 -date "2018/02/07" # modo campaña

################### MODO NORMAL #################
#################################################
#python RTDI_OUT_HF.py -path /home/hfuser/HFA -C 0 -ii 6 -f 2.72216796875 -code 0 -lo 11 -ch 1 -date "2018/04/15" # modo normal
python RTDI_OUT_HF.py -path /home/hfuser/HFB -C 0 -ii 6 -f 2.72216796875 -code 0 -lo 12 -ch 1 -date "2018/06/22" # modo normal

