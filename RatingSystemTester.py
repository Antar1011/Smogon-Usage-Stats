#!/usr/bin/python
# -*- coding: latin-1 -*-

import sys
import gzip
import json
import math
import cPickle as pickle

systems = sys.argv[1].split(',')

try:
	ratingSystems={}
	for system in systems:
		ratingSystems[system] = __import__(system)
except:
	sys.stderr.write('Incorrect syntax.\n')
	sys.stderr.write('Correct usage:\n')
	sys.stderr.write('\tpython RatingSystemTester.py SYSTEMS [-w] FILES...\n')
	sys.stderr.write('Example:\n')
	sys.stderr.write('\tpython RatingSystemTester.py Elo,Glicko2 -w ratingTests/lc-201401 ratingTests/lc-201401.csv\n')
	sys.exit(1)

ratings={}

winfiles={}
if sys.argv[2] == '-w':
	base=sys.argv[3]+'-'
	for system in systems:
		winfiles[system]=open(base+system+'.csv','w')
	idx=4
else:
	idx=2

date=''
while idx<len(sys.argv):
	raw = open(sys.argv[idx]).read()

	raw=raw.split('\n')
	
	for line in raw:
		battle=line.split(',')
		if len(battle)<3:
			print line
			continue

		if battle[0] != date:
			for player in ratings.keys():
				for system in systems:
					ratings[player][system]=ratingSystems[system].newRatingPeriod(ratings[player][system])
			date=battle[0]
		
		for p in [1,2]:
			if battle[p] not in ratings.keys():
				newScore={'nBattles':0.0,'nWins':0.0}
				for system in systems:
					newScore[system]=ratingSystems[system].newPlayer()
				ratings[battle[p]]=newScore
			ratings[battle[p]]['nBattles']+=1
			
		ratings[battle[1]]['nWins']+=2.0-float(battle[3])
		ratings[battle[2]]['nWins']+=float(battle[3])-1.0
		for system in systems:
			ratings[battle[1]][system],ratings[battle[2]][system],E=ratingSystems[system].update(ratings[battle[1]][system],ratings[battle[2]][system],battle[3])
			if system in winfiles.keys():
				winfile=winfiles[system]
				if int(battle[3]) == 1:
					score=1.0
				elif int(battle[3]) == 2:
					score=0.0
				else: #if outcome == 0
					score=0.5
				winfile.write(str(E)+','+str(score)+'\n')

	idx+=1
if winfile is not None:
	winfile.close()

for player in ratings.keys():
	for system in systems:
		ratings[player][system]=ratingSystems[system].newRatingPeriod(ratings[player][system])

printme='Username,nBattles,nWins'
for system in systems:
	printme+=','+ratingSystems[system].headers()
print printme

for player in ratings.keys():
	printme=player+','+str(ratings[player]['nBattles'])+','+str(ratings[player]['nWins'])
	for system in systems:
		printme+=','+ratingSystems[system].printRating(ratings[player][system])
	print printme
