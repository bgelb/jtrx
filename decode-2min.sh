#!/bin/bash

WORKDIR=working
DATADIR=data
MYCALL=N1VF/L
MYGRID=CM97AI

export XDG_RUNTIME_DIR="/run/user/1000"

cd $WORKDIR

while [ 1 ] ; do
	sleep $[ 120 - $(date +%s) % 120  ]
	TS=`date +%s`
	PERIOD=`date -d@$TS +%y%m%d_%H%M`
	
	# calc last two one-minute data files to grab
	PERIOD_PREV_1=`date -d@$(($TS-60)) +%y%m%d_%H%M`
	PERIOD_PREV_2=`date -d@$(($TS-120)) +%y%m%d_%H%M`
	
	sleep 1 # wait for dat file to get flushed out
	
	echo "`date`: Processing period $PERIOD_PREV_2..." >> decode.log
	cat ../$DATADIR/$PERIOD_PREV_2.dat ../$DATADIR/$PERIOD_PREV_1.dat > 2min_temp.dat
	/usr/bin/python ../towav.py --infile 2min_temp.dat --outfile $PERIOD_PREV_2.wav
	/usr/bin/wsprd -f 0.4742 ch1_$PERIOD_PREV_2.wav >> decode.log
	rm ch1_$PERIOD_PREV_2.wav
	rm ch2_$PERIOD_PREV_2.wav
	rm 2min_temp.dat
	
	FILESIZE=$(stat -c%s "wspr_spots.txt")
	if [ $FILESIZE -ne 0 ] ; then
	
	        # add the spots to a temporary file used for uploading to wsprnet.org
	        cat wspr_spots.txt >> wsprdsum.out
	
	        # upload the spots
	        echo "`date`: upload by curl" >> decode.log
	        /usr/bin/curl -F allmept=@wsprdsum.out -F call=${MYCALL} -F grid=${MYGRID} http://wsprnet.org/meptspots.php >> decode.log;
	        RESULT=$?
	
	        # check if curl uploaded the data successfully
	        # delete only if uploaded
	        if [ $RESULT -eq 0 ] ; then
	                # data uploaded, delete them
	                echo "`date`: Upload OK, deleting" >> decode.log
	                rm wsprdsum.out
	        fi
	        echo "`date`: curl result: $RESULT , done." >> decode.log
	fi
done
