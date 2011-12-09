#!/bin/bash
mkdir Activity
rm -r Activity/*
mkdir Activity/MonthLong/
mkdir Activity/Hourly/
mkdir Activity/Daily/

maxjobs=6 #set to number of multiprocessors

for j in Logs/*
do
	for  i in "$j"/*
	do
		jobcnt=(`jobs -p`)
		while [ ${#jobcnt[@]} -ge $maxjobs ]
		do
			jobcnt=(`jobs -p`)
		done
		echo Processing $i
		python ../Activity.py "$i"
	done
done

for i in Activity/*.txt; do python ../ActivityPlot.py "$i" -MonthLong > "Activity/MonthLong/${i/Activity}" ; done
for i in Activity/*.txt; do python ../ActivityPlot.py "$i" -Daily > "Activity/Daily/${i/Activity}" ; done
for i in Activity/*.txt; do python ../ActivityPlot.py "$i" -Hourly > "Activity/Hourly/${i/Activity}" ; done
