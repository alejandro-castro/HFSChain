#!/bin/bash
echo "HFA0_C0"
python PLOT_HF.py -online 0 -f 2.72 -code 0 -date "2018/02/15"
echo "HFA0_C2"
python PLOT_HF.py -online 0 -f 2.72 -code 2 -date "2018/02/15"

echo "HFA1_C0"
python PLOT_HF.py -online 0 -f 3.64 -code 0 -date "2018/02/15"

echo "HFA1_C2"
python PLOT_HF.py -online 0 -f 3.64 -code 2 -date "2018/02/15"
