#!/bin/bash
echo "INICIANDO SECUENCIA DE CONSOLAS"

echo "EJECUTANDO PROGRAMA DE ENVIO"
cd /home/igp-114/TestReduccionDatos_Implementado/hfschain/schainroot/source/schainpy/SendingScripts
#The first parameter is the location
#The second parameter of this script is going to be any of the following strings: params, out, rtdi
#That string is going to pass through to the send_SCP.py and set the paths to send the correct type of result
screen -S "ENVIO_WEB_PARAMS" -d -m ./sendResults_SCP.sh  0  1  2  /home/igp-114/Pictures/   $1    params
screen -S "ENVIO_WEB_RTDI" -d -m ./sendResults_SCP.sh  0  1  2  /home/igp-114/   $1    rtdi
screen -S "ENVIO_WEB_OUT" -d -m ./sendResults_SCP.sh  0  1  2  /home/igp-114/   $1    out
