#!/bin/bash
cd $HOME/TestReduccionDatos_Implementado/hfschain/schainroot/source/schainpy/test

source $HOME/TestReduccionDatos_Implementado/bin/activate

#El primer parametro del PLOT_db is the pathin and the second is the location of the station
export HF_LOCATION="11"
echo "Starting Reduction of Data of JRO A station"
screen -S "REDUCTION_HFA" -d -m ./PLOT_db.sh "$HOME/HFA/" 11
sleep 1

export HF_LOCATION="12"
#Los directorios donde estan los HDF5 colocados aqui siempre deben terminar en /
echo "Starting Reduction of Data of JRO B station"
screen -S "REDUCTION_HFB" -d -m ./PLOT_db.sh "$HOME/HFB/" 12
sleep 1


while [ screen -list | grep -q "REDUCTION" ]
do
	sleep 3
	echo "Waiting for Reduction to finish"
done

./OrderNewHDF5Files.sh "JRO_A"
./OrderNewHDF5Files.sh "JRO_B"


echo "Plotting the new RTDI from moments"
screen -S "PLOT_RTDI_A_FROM_REDUCED" -d -m ./PLOT_RTDI_A.sh

sleep 1
screen -S "PLOT_RTDI_A_FROM_REDUCED" -d -m ./PLOT_RTDI_B.sh
