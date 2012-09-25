#!/bin/bash

logFolder = "/backup/smogon/showdown/logs" #edit this!

mkdir "$(date -d 'yesterday' +%Y-%m)/Raw"
cd "$(date -d 'yesterday' +%Y-%m)"

for tier in "balancedhackmons" "cap" "challengecup" "dwou" "dwubers" "glitchmons" "hackmons" "lc" "nu" "ou" "oususpecttest" "randombattle" "ru" "ubers" "uu"
do
	if [ -d "$logFolder/$(date -d 'yesterday' +%Y-%m)/$tier/$(date -d 'yesterday' +%Y-%m-%d)" ]; then
	for i in $logFolder/"$(date -d 'yesterday' +%Y-%m)"/$tier/"$(date -d 'yesterday' +%Y-%m-%d)"/*
	do
		#echo Processing $i
		python ../LogReaderOnPS.py "$i" "$tier"
	done
	fi
done

if (($(date -d 'today' +%d) == 1))
then
	./MonthlyScript.sh
done
