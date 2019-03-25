#!/bin/bash
echo "HFA0_C0"
python PLOT_HF.py -online 0 -f 2.72216796875 -code 0 -lo  41

echo "HFA0_C1"
python PLOT_HF.py -online 0 -f 2.72216796875 -code 1 -lo  41

echo "HFA0_C2"
python PLOT_HF.py -online 0 -f 2.72216796875 -code 2 -lo 41

echo "HFA1_C0"
python PLOT_HF.py -online 0 -f 3.64990234375 -code 0 -lo 41

echo "HFA1_C1"
python PLOT_HF.py -online 0 -f 3.64990234375 -code 1 -lo  41

echo "HFA1_C2"
python PLOT_HF.py -online 0 -f 3.64990234375 -code 2 -lo 41

