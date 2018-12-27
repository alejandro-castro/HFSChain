#!/bin/sh



filename = "testRawData.py"
output = "output"

python -m cProfile -o $output $filename

gprof2dot -f pstats $output.pstats | dot -Tpng -o $output.png

#sino probar esto : ejecutar esto antes python -m cProfile -o profile.pstats xxxx.py arg1 arg2 argN....
#2do ejecutar esta linea : gprof2dot -f pstats profile.pstats | dot -Tpdf -o profile.pdf


