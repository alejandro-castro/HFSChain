#!/bin/bash
echo "INICIANDO SECUENCIA DE CONSOLAS"

echo "EJECUTANDO PROGRAMA DE ENVIO"

screen -S "ENVIO_WEB" -d -m ./sendResults_SCP.sh 0 1 2
