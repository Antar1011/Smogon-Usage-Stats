#!/bin/bash
mkdir Activity
rm Activity/*

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

for i in Activity/*; do python ../StatCounterOnCrack.py "$i" > "Activity/Hourly/${i/Activity}" ; done
