#!/bin/bash

####################################################################################
################################## envio por SCP ###################################
echo "Sending results"
python send_SCP.py -code $1 -path $4 -lo $5 -type $6
python send_SCP.py -code $2 -path $4 -lo $5 -type $6
python send_SCP.py -code $3 -path $4 -lo $5 -type $6
###################################################################################
