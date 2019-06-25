#!/bin/bash

if [ $3 = "0" ]
then
	echo "Modo normal"
	python RTDI_OUT_HF.py -path $1 -f 2.72216796875 -C 0 -ii 6 -code 0 -lo $2 -ch 0 -date $4
	python RTDI_OUT_HF.py -path $1 -f 2.72216796875 -C 0 -ii 6 -code 1 -lo $2 -ch 0 -date $4
	python RTDI_OUT_HF.py -path $1 -f 2.72216796875 -C 0 -ii 6 -code 2 -lo $2 -ch 0 -date $4

	python RTDI_OUT_HF.py -path $1 -f 3.64990234375 -C 0 -ii 6 -code 0 -lo $2 -ch 0 -date $4
	python RTDI_OUT_HF.py -path $1 -f 3.64990234375 -C 0 -ii 6 -code 1 -lo $2 -ch 0 -date $4
	python RTDI_OUT_HF.py -path $1 -f 3.64990234375 -C 0 -ii 6 -code 2 -lo $2 -ch 0 -date $4


	python RTDI_OUT_HF.py -path $1 -f 2.72216796875 -C 0 -ii 6 -code 0 -lo $2 -ch 1 -date $4
	python RTDI_OUT_HF.py -path $1 -f 2.72216796875 -C 0 -ii 6 -code 1 -lo $2 -ch 1 -date $4
	python RTDI_OUT_HF.py -path $1 -f 2.72216796875 -C 0 -ii 6 -code 2 -lo $2 -ch 1 -date $4

	python RTDI_OUT_HF.py -path $1 -f 3.64990234375 -C 0 -ii 6 -code 0 -lo $2 -ch 1 -date $4
	python RTDI_OUT_HF.py -path $1 -f 3.64990234375 -C 0 -ii 6 -code 1 -lo $2 -ch 1 -date $4
	python RTDI_OUT_HF.py -path $1 -f 3.64990234375 -C 0 -ii 6 -code 2 -lo $2 -ch 1 -date $4
elif [ $3 = "1" ]
then
	echo "Modo campaña"
	python RTDI_OUT_HF.py -path $1 -f 2.72216796875 -C 1 -ii 0 -code 0 -lo $2 -ch 0 -date $4
	python RTDI_OUT_HF.py -path $1 -f 2.72216796875 -C 1 -ii 0 -code 1 -lo $2 -ch 0 -date $4
	python RTDI_OUT_HF.py -path $1 -f 2.72216796875 -C 1 -ii 0 -code 2 -lo $2 -ch 0 -date $4

	python RTDI_OUT_HF.py -path $1 -f 3.64990234375 -C 1 -ii 0 -code 0 -lo $2 -ch 0 -date $4
	python RTDI_OUT_HF.py -path $1 -f 3.64990234375 -C 1 -ii 0 -code 1 -lo $2 -ch 0 -date $4
	python RTDI_OUT_HF.py -path $1 -f 3.64990234375 -C 1 -ii 0 -code 2 -lo $2 -ch 0 -date $4


	python RTDI_OUT_HF.py -path $1 -f 2.72216796875 -C 1 -ii 0 -code 0 -lo $2 -ch 1 -date $4
	python RTDI_OUT_HF.py -path $1 -f 2.72216796875 -C 1 -ii 0 -code 1 -lo $2 -ch 1 -date $4
	python RTDI_OUT_HF.py -path $1 -f 2.72216796875 -C 1 -ii 0 -code 2 -lo $2 -ch 1 -date $4

	python RTDI_OUT_HF.py -path $1 -f 3.64990234375 -C 1 -ii 0 -code 0 -lo $2 -ch 1 -date $4
	python RTDI_OUT_HF.py -path $1 -f 3.64990234375 -C 1 -ii 0 -code 1 -lo $2 -ch 1 -date $4
	python RTDI_OUT_HF.py -path $1 -f 3.64990234375 -C 1 -ii 0 -code 2 -lo $2 -ch 1 -date $4

else
	echo "Error en el flag de campaña en PLOT_RTDI.sh"
	exit 1
fi
