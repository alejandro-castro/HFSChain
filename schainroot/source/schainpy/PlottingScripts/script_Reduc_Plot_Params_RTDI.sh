#!/bin/bash
cd $HOME/TestReduccionDatos_Implementado/hfschain/schainroot/source/schainpy/PlottingScripts

source $HOME/TestReduccionDatos_Implementado/bin/activate

#El primer parametro del GenerateMoments is the pathin and the second is the location of the station
echo "Starting Reduction of Data of JRO A station"
screen -S "REDUCTION_HFA" -d -m ./GenerateMoments.sh "/media/igp-114/PROCDATA" 11
sleep 1


COUNT=$(screen -list | grep -c "REDUCTION")
while [  $COUNT != "0" ]
do
	sleep 3
	echo "Waiting for Reduction to finish"
	COUNT=$(screen -list | grep -c "REDUCTION")
done

###################Plotting Parameters#################################################3

#El primer parametro del GenerateMoments is the pathin and the second is the location of the station
echo "Plotting Parameters from Reducted Data"
screen -S "PlottingParam" -d -m ./Plot_db.sh "$HOME/Pictures/" 11
sleep 1

COUNT=$(screen -list | grep -c "PlottingParam")
while [  $COUNT != "0" ]
do
	sleep 3
	echo "Waiting for PlottingParam to finish"
	COUNT=$(screen -list | grep -c "PlottingParam")
done


echo "Plotting the new RTDI from moments"
screen -S "PLOT_RTDI_A_FROM_REDUCED" -d -m ./PLOT_RTDI.sh $HOME/Pictures/ 11

sleep 1
