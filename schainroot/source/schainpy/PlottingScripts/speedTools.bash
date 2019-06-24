#Use this script in order to find the slowest module or function in your python code.
#Reference: http://lukauskas.co.uk/articles/2014/02/12/how-to-make-python-faster-without-trying-that-much/

#sudo apt-get install graphviz
#pip install gprof2dot



#!/bin/sh

script = "PLOT_param.py"
output = "profile.pdf"

python -m cProfile -o profile.pstats $script

gprof2dot -f pstats profile.pstats | dot -Tpdf -o $output
