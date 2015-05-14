#!/bin/bash
#This file is included solely to be used as an example. It will likely need to be heavily modified from month to month
#(or from run to run)

logFolder=/home/ps/showdown/logs
month="2015-04"

rm -r Raw
mkdir Raw

for day in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30
do
	for i in $logFolder/$month/*
	do
		tier=$(basename $i)
		if [ -d $logFolder/$month/$tier/$month-$day ]; then
			echo Processing $tier/$month-$day
			pypy batchLogReader.py $logFolder/$month/$tier/$month-$day/ $tier
		fi
	done
done
echo $(date)
./MonthlyAnalysis.sh
echo $(date)
