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

	PURGE_TS=$(($TS-172800))
	PURGE_DATE=`date -d@$PURGE_TS +%y%m%d_`

	# calc last two one-minute data files to grab
	PERIOD_PREV_1=`date -d@$(($TS-60)) +%y%m%d_%H%M`
	PERIOD_PREV_2=`date -d@$(($TS-120)) +%y%m%d_%H%M`

	sleep 1 # wait for dat file to get flushed out

	echo "`date`: Processing period $PERIOD_PREV_2..." >> decode.log
	cat ../$DATADIR/$PERIOD_PREV_2.dat ../$DATADIR/$PERIOD_PREV_1.dat > 2min_temp.dat
	/usr/bin/python ../towav.py --infile 2min_temp.dat --outfile $PERIOD_PREV_2.wav

	# magic phase/gain values
	/usr/bin/python ../phase.py --infile 2min_temp.dat --phi 245.0 --gain 4.85
	mv combined_out.wav ch3_${PERIOD_PREV_2}.wav

	for i in {1..3}
	do
		echo "`date`: Processing Channel $i" >> decode.log
		/usr/bin/wsprd -d -f 0.4742 ch${i}_${PERIOD_PREV_2}.wav >> decode.log
		FILESIZE=$(stat -c%s "wspr_spots.txt")
		if [ $FILESIZE -ne 0 ] ; then

		        # add the spots to a temporary file used for uploading to wsprnet.org
		        cat wspr_spots.txt >> wsprdsum_ch$i.out

		        # upload the spots
		        echo "`date`: upload by curl" >> decode.log
		        /usr/bin/curl -m 10 -F allmept=@wsprdsum_ch$i.out -F call=${MYCALL}${i} -F grid=${MYGRID} http://wsprnet.org/meptspots.php >> decode.log;
		        RESULT=$?

		        # check if curl uploaded the data successfully
		        # delete only if uploaded
		        if [ $RESULT -eq 0 ] ; then
		                # data uploaded, delete them
		                echo "`date`: Upload OK, deleting" >> decode.log
		                rm wsprdsum_ch$i.out
		        fi
		        echo "`date`: curl result: $RESULT , done." >> decode.log
		fi
	done

	rm ch1_$PERIOD_PREV_2.wav
	rm ch2_$PERIOD_PREV_2.wav
	rm ch3_$PERIOD_PREV_2.wav
	rm 2min_temp.dat

	echo "`date`: Purging $PURGE_DATE*" >> decode.log
	rm ../$DATADIR/$PURGE_DATE*
done
