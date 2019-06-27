#!/bin/bash

#El primer parametro de este script es la locacion
#El segundo parametro de este script es un flag de campaña
#El tercero parametro es la fecha y es opcional.

cd $HOME/TestReduccionDatos_Implementado/hfschain/schainroot/source/schainpy/PlottingScripts

source $HOME/TestReduccionDatos_Implementado/bin/activate
export DISPLAY=":0.0"
#El primer parametro de todos los scripts llamados es la ubicacion de la data y el segundo es la locacion de la estacion
#El tercero es un flag de campaña,1 campaña, 0 modo normal
#Se puede usar un cuarto parametro para la fecha, si se le puso fecha al script general Reduc_PLot_...
#se pasa esa fecha si no pone por defecto la fecha del dia anterior

date_to_process=${3:-$(date -d "yesterday" +"%Y/%m/%d")} #Comentar si se desea procesar otra fecha
#date_to_process="2018/03/20" Modificar y quitar el comentario si se desea procesar otra fecha
###################Generating Parameters Data#################################################3

echo "Starting Reduction of Data of JRO A station"
screen -S "REDUCTION_HF" -d -m ./GenerateMoments.sh "/media/igp-114/PROCDATA" $1 $2 $date_to_process
sleep 1


#Espera a que los nuevos archivos de momentos hayan terminado de generarse
COUNT=$(screen -list | grep -c "REDUCTION_HF")
while [  $COUNT != "0" ]
do
	sleep 3
	echo "Waiting for Reduction to finish"
	COUNT=$(screen -list | grep -c "REDUCTION")
done

###################Plotting Parameters#################################################3

echo "Plotting Parameters from Reducted Data"
screen -S "PlottingParam" -d -m ./Plot_db.sh "$HOME/Pictures/" $1 $2 $date_to_process
sleep 1

COUNT=$(screen -list | grep -c "PlottingParam")
while [  $COUNT != "0" ]
do
	sleep 3
	echo "Waiting for PlottingParam to finish"
	COUNT=$(screen -list | grep -c "PlottingParam")
done

###################Plotting RTDI#################################################3

echo "Plotting the new RTDI from moments"
screen -S "PLOT_RTDI_FROM_REDUCED" -d -m ./PLOT_RTDI.sh $HOME/Pictures/ $1 $2 $date_to_process

sleep 1


COUNT=$(screen -list | grep -c "PLOT_RTDI_FROM_REDUCED")
while [  $COUNT != "0" ]
do
	sleep 3
	echo "Waiting for RTDI Plots to finish"
	COUNT=$(screen -list | grep -c "PLOT_RTDI_FROM_REDUCED")
done


cd $HOME/TestReduccionDatos_Implementado/hfschain/schainroot/source/schainpy/SendingScripts
./sending_script.sh $1
