#!/bin/bash

/usr/bin/python -u towav.py --infile $1
wsprd -d ch1_out.wav
wsprd -d ch2_out.wav

for g in `seq 4.5 .1 5.5`
do
	for phi in `seq 148 .1 152`
	do
		/usr/bin/python -u phase.py --infile $1 --phi $phi --gain $g
		echo "phi=$phi gain=$g `wsprd combined_out.wav | grep _out`"
	done
done
