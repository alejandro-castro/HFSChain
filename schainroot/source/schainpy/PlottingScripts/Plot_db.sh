#!/bin/bash
if [ $3 = "0" ]
then
	echo "Modo normal"
	echo "HFA0_C0"
	python PlotParam.py  -path $1 -f 2.72216796875  -C 0 -ii 6 -online 0 -code 0 -lo $2 -date $4
	echo "HFA0_C1"
	python PlotParam.py  -path $1 -f 2.72216796875  -C 0 -ii 6 -online 0 -code 1 -lo $2 -date $4
	echo "HFA0_C2"
	python PlotParam.py  -path $1 -f 2.72216796875  -C 0 -ii 6 -online 0 -code 2 -lo $2 -date $4


	echo "HFA1_C0"
	python PlotParam.py  -path $1 -f 3.64990234375 -C 0 -ii 6 -online 0 -code 0 -lo $2 -date $4
	echo "HFA1_C1"
	python PlotParam.py  -path $1 -f 3.64990234375 -C 0 -ii 6 -online 0 -code 1 -lo $2 -date $4
	echo "HFA1_C2"
	python PlotParam.py  -path $1 -f 3.64990234375 -C 0 -ii 6 -online 0 -code 2 -lo $2 -date $4
elif [ $3 = "1" ]
then
	echo "Modo campaña"
	echo "HFA0_C0"
	python PlotParam.py  -path $1 -f 2.72216796875  -C 1 -ii 0 -online 0 -code 0 -lo $2 -date $4
	echo "HFA0_C1"
	python PlotParam.py  -path $1 -f 2.72216796875  -C 1 -ii 0 -online 0 -code 1 -lo $2 -date $4
	echo "HFA0_C2"
	python PlotParam.py  -path $1 -f 2.72216796875  -C 1 -ii 0 -online 0 -code 2 -lo $2 -date $4


	echo "HFA1_C0"
	python PlotParam.py  -path $1 -f 3.64990234375 -C 1 -ii 0 -online 0 -code 0 -lo $2 -date $4
	echo "HFA1_C1"
	python PlotParam.py  -path $1 -f 3.64990234375 -C 1 -ii 0 -online 0 -code 1 -lo $2 -date $4
	echo "HFA1_C2"
	python PlotParam.py  -path $1 -f 3.64990234375 -C 1 -ii 0 -online 0 -code 2 -lo $2 -date $4
else
	echo "Error en el flag de campaña en Plot_db.sh"
	exit 1
fi
