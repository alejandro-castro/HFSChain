#!/bin/sh

filename = "testRawData.py"
output = "output"

python -m cProfile -o $output $filename

gprof2dot -f pstats $output.pstats | dot -Tpng -o $output.png