#!/bin/bash

/usr/bin/python -u towav.py --infile $1
wsprd ch1_out.wav
wsprd ch2_out.wav

for g in `seq -0.5 .1 0.5`
do
	for phi in `seq 60 1 90`
	do
		/usr/bin/python -u phase.py --infile $1 --phi $phi --gain $g
		echo "phi=$phi gain=$g `wsprd combined_out.wav | grep _out`"
	done
done
