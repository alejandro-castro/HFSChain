#!/bin/bash

#The only parameter of this file is the station name that should be JROA or JROB for example

stations="sp01_f0 sp01_f1 sp11_f0 sp11_f1 sp21_f0 sp21_f1"

for station in $stations; do
	for doy_folder in "$HOME/Pictures/GRAPHICS_SCHAIN_$1/$station/param"/d*
	do
		day=$(basename $doy_folder)
		if [ ! -d $HOME/Pictures/$1_HDF5/$day/ ]; then
			mkdir  $HOME/Pictures/$1_HDF5/$day/
		fi

		if [ ! -d $HOME/Pictures/$1_HDF5/$day/$station/ ]; then
			mkdir  $HOME/Pictures/$1_HDF5/$day/$station
		fi

		mv $doy_folder/* $HOME/Pictures/$1_HDF5/$day/$station/
	done
done
