#!/bin/bash

WORKDIR=working
DATADIR=data
MYCALL=N1VF/L
MYGRID=CM97AI
OLD_PHASE_ARGS="--gain 0 --phi 0"

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

	for i in {1..2}
	do
		echo "`date`: Processing Channel $i" >> decode.log
		/usr/bin/wsprd -d -f 0.4742 ch${i}_${PERIOD_PREV_2}.wav >> decode.log
		sed -i '/N1VF/ d' wspr_spots.txt
		FILESIZE=$(stat -c%s "wspr_spots.txt")
		if [ $FILESIZE -ne 0 ] ; then

		        # add the spots to a temporary file used for uploading to wsprnet.org
		        cat wspr_spots.txt >> wsprdsum_ch$i.out

		        # upload the spots
			cat wsprdsum_ch$i.out
		        echo "`date`: upload wspr by curl" >> decode.log
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
		/usr/bin/jt9 -W -p 120 -L 1400 -H 1600 -f 1500 -F 100 -d 3 ch${i}_${PERIOD_PREV_2}.wav >> decode.log
		FILESIZE=$(stat -c%s "decoded.txt")
                if [ $FILESIZE -ne 0 ] ; then
                        echo "nonzero decoded.txt" >> decode.log
                        cat decoded.txt >> decode.log
                        # add the spots to a temporary file used for uploading to wsprnet.org
                        #cat decoded.txt | awk '{ print $1,$2,$3,$4,$5,$6,$7,$8,$9,0,3 }' >> wsprdsum_ch$i.out
                        cat decoded.txt | awk -v ts="${PERIOD_PREV_2}" '{ rf = ($5+474200) / 1000000 ; print ts,$2,$3,$4,rf,$7,$8,$9,0,3 }' >> wsprdsum_ch$i.out
                        rm decoded.txt

                        # upload the spots
			                  cat wsprdsum_ch$i.out >> decode.log
                        echo "`date`: upload fst4w by curl" >> decode.log
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

	echo "running gain/phase search" >> decode.log
	PHASE_ARGS=`/usr/bin/python ../scripts/search.py --infile 2min_temp.dat | tee -a decode.log | head -n1 | sed 's/^.*gain=\([0-9]*\), phi=\([0-9]*\).*$/--gain \1 --phi \2/'`
	echo "phase.py $PHASE_ARGS" >> decode.log
	/usr/bin/python ../phase.py --infile 2min_temp.dat $PHASE_ARGS
	mv combined_out.wav ch3_${PERIOD_PREV_2}.wav

	for i in {3..3}
	do
		echo "`date`: Processing Channel $i" >> decode.log
		/usr/bin/wsprd -d -f 0.4742 ch${i}_${PERIOD_PREV_2}.wav >> decode.log
		sed -i '/N1VF/ d' wspr_spots.txt
		FILESIZE=$(stat -c%s "wspr_spots.txt")
		if [ $FILESIZE -ne 0 ] ; then
			echo "`date`: saving phase args $PHASE_ARGS" >> decode.log
			OLD_PHASE_ARGS=$PHASE_ARGS
		        # add the spots to a temporary file used for uploading to wsprnet.org
		        cat wspr_spots.txt >> wsprdsum_ch$i.out

		        # upload the spots
		        echo "`date`: upload wspr by curl" >> decode.log
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
