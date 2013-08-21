#!/usr/bin/python
# -*- coding: latin-1 -*-

import gzip
import sys
import json

from common import *

tier = str(sys.argv[1])

maxRD = 100
if (len(sys.argv) > 2):
	maxRD = float(sys.argv[2])

binSize = 0.01
if (len(sys.argv) > 3):
	binSize = float(sys.argv[3])
	
filename="Raw/"+tier#+".txt"
file = gzip.open(filename,'rb')
raw = file.read()
file.close()

raw=raw.split('][')
for i in range(len(raw)):
	if (i>0):
		raw[i]='['+raw[i]
	if (i<len(raw)-1):
		raw[i]=raw[i]+']'

bins=[]
binCenter=0.5+binSize/2
while binCenter < 1.0:
	bins.append([binCenter,0,0])
	binCenter = binCenter+binSize

for line in raw:
	battles = json.loads(line)

	for battle in battles:

		if 'rating' not in battle['p1'].keys() or 'rating' not in battle['p1'].keys() or 'outcome' not in battle['p1'].keys():
			continue
		if battle['p1']['rating']['rd'] <= maxRD and battle['p2']['rating']['rd'] <= maxRD:
			if battle['p1']['rating']['r'] > battle['p2']['rating']['r']:
				probWin = victoryChance(battle['p1']['rating']['r'],battle['p1']['rating']['rd'],battle['p2']['rating']['r'],battle['p2']['rating']['rd'])
				betterPlayer='p1'
			else:
				probWin = victoryChance(battle['p2']['rating']['r'],battle['p2']['rating']['rd'],battle['p1']['rating']['r'],battle['p1']['rating']['rd'])
				betterPlayer='p2'				
			for i in xrange(len(bins)):
				if probWin < bins[i][0]+binSize/2:
					bins[i][1]=bins[i][1]+probWin
					if battle[betterPlayer]['outcome'] == 'win':
						bins[i][2]=bins[i][2]+1
					break

for bin in bins:
	print bin[0],bin[1],bin[2]
	
