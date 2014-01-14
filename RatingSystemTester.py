#!/usr/bin/python
# -*- coding: latin-1 -*-

import sys
import gzip
import json
import math
import cPickle as pickle

def incorrectSyntax():
	sys.stderr.write('Incorrect syntax.\n')
	sys.stderr.write('Correct usage:\n')
	sys.stderr.write('\tpython RatingSystemTester.py SYSTEMS [-n] [-w prefix] FILES...\n')
	sys.stderr.write('OPTIONS:\n')
	sys.stderr.write('\t-w prefix\tWrite "win" files listing actual vs. expected outcomes.\n')
	sys.stderr.write('\t\t\tA file is generated for each system with a name starting\n')
	sys.stderr.write('\t\t\twith the specified prefix.\n')
	sys.stderr.write('\t-n\t\tIf match ended in a forfeit, do not update ratings.\n')
	sys.stderr.write('Example:\n')
	sys.stderr.write('\tpython RatingSystemTester.py Elo,Glicko2 -w ratingTests/lc-201401 ratingTests/lc-201401.csv\n')
	sys.exit(1)

daysPerRatingPeriod=1

systems = sys.argv[1].split(',')

try:
	ratingSystems={}
	for system in systems:
		ratingSystems[system] = __import__(system)
except:
	incorrectSyntax()

ratings={}

winfiles={}
noforfeits=False

idx=2
while sys.argv[idx].startswith('-'):
	if (sys.argv[idx] == '-w'):
		base=sys.argv[idx+1]+'-'
		for system in systems:
			winfiles[system]=open(base+system+'.csv','w')
		idx+=2
	elif (sys.argv[idx] == '-n'):
		noforfeits=True
		idx+=1
	else:
		incorrectSyntax()

date=''
bprpfile=open(base+'brpr.csv','w')

i=0
while idx<len(sys.argv):
	for line in open(sys.argv[idx]).readlines():
		battle=line.split(',')
		if len(battle)<8:
			continue

		if battle[6] != 'normal' and noforfeits:
			continue

		if battle[0] != date:
			i+=1
			if (i == daysPerRatingPeriod):
				for player in ratings.keys():
					bprpfile.write(str(ratings[player]['battlesInRatingPeriod'])+'\n')
					ratings[player]['battlesInRatingPeriod']=0
					for system in systems:
						ratings[player][system]=ratingSystems[system].newRatingPeriod(ratings[player][system])
				i=0
			date=battle[0]
		
		for p in [1,3]:
			if battle[p] not in ratings.keys():
				newScore={'nBattles':0.0,'nWins':0.0,'battlesInRatingPeriod':0.0}
				for system in systems:
					newScore[system]=ratingSystems[system].newPlayer()
				ratings[battle[p]]=newScore
			ratings[battle[p]]['nBattles']+=1
			ratings[battle[p]]['battlesInRatingPeriod']+=1
			
		ratings[battle[1]]['nWins']+=2.0-float(battle[5])
		ratings[battle[3]]['nWins']+=float(battle[5])-1.0

		for system in systems:
			ratings[battle[1]][system],ratings[battle[3]][system],E=ratingSystems[system].update(ratings[battle[1]][system],ratings[battle[3]][system],battle[5])
			if system in winfiles.keys():
				winfile=winfiles[system]
				if int(battle[5]) == 1:
					score=1.0
				elif int(battle[5]) == 2:
					score=0.0
				else: #if outcome == 0
					score=0.5
				winfile.write(str(E)+','+str(score)+'\n')

	idx+=1
try:
	for winfile in winfiles.values():
		winfile.close()

	bprpfile.close()
except:
	sys.err.write("I dunno what's going on.\n")

for player in ratings.keys():
	ratings[player]['battlesInRatingPeriod']=0
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
