#!/usr/bin/python
# -*- coding: latin-1 -*-

import sys
import gzip
import json
import math
import cPickle as pickle

systems = sys.argv[1].split(',')
try:
	ladderRatingSystem={}
	for system in systems:
		ladderRatingSystem[system] = __import__(system)
except:
	sys.stderr.write('Incorrect syntax.\n')
	sys.stderr.write('Correct usage:\n')
	sys.stderr.write('\tpython ladderRatingTester.py SYSTEMS FILES... [-t TRAJECTORYFILE]\n')
	sys.stderr.write('Example:\n')
	sys.stderr.write('\tpython ladderRatingTester.py AX1,AX2 2013-07/Raw/ou 2013-08/Raw/ou -t trajectories.pickle\n')
	sys.exit(1)

ladder={}
metrics=set(['r','rd','rpr','rprd'])
trajectories={}
trajectoriesSaveFile=False
wltCounts={}

idx=2
while idx<len(sys.argv):
	filename=sys.argv[idx]
	if filename == '-t':
		trajectoriesSaveFile=sys.argv[idx+1]
		idx=idx+2
		continue
		
	file = gzip.open(filename,'rb')
	raw = file.read()
	file.close()

	raw=raw.split('][')
	for i in range(len(raw)):
		if (i>0):
			raw[i]='['+raw[i]
		if (i<len(raw)-1):
			raw[i]+=']'

	for line in raw:
		battles = json.loads(line)
		for battle in battles:
			ratings={}
			scores={}
			winner=0
			ladderError = False
			for player in ['p1','p2']:
				if 'rating' in battle[player].keys():
					if metrics.issubset(battle[player]['rating'].keys()):
						if battle[player]['rating']['rd'] != 0.0 and battle[player]['rating']['rprd'] != 0.0:
							ratings[player]={}
							for metric in metrics:
								ratings[player][metric]=battle[player]['rating'][metric]
				if player not in ratings.keys(): #in the event of a ladder error
					ladderError = True
					ratings[player]={}
					ratings[player]['r']=ratings[player]['rpr']=1500.0
					ratings[player]['rd']=ratings[player]['rprd']=350.0
				scores[player]={}
				if battle[player]['trainer'] in ladder.keys():
					for system in systems:
						scores[player][system]=ladder[battle[player]['trainer']]['scores'][system]
				else:
					ladder[battle[player]['trainer']]={'rating':ratings[player]}
					for system in systems:
						scores[player][system]=ladderRatingSystem[system].newPlayer()
					trajectories[battle[player]['trainer']]=[]
					wltCounts[battle[player]['trainer']]=[0,0,0]

			if 'outcome' in battle['p1'].keys():
				if battle['p1']['outcome'] == 'win':
					winner=1
					wltCounts[battle['p1']['trainer']][0]+=1
					wltCounts[battle['p2']['trainer']][1]+=1
				elif battle['p1']['outcome'] == 'loss':
					winner=2
					wltCounts[battle['p2']['trainer']][0]+=1
					wltCounts[battle['p1']['trainer']][1]+=1
				else:
					wltCounts[battle['p1']['trainer']][2]+=1
					wltCounts[battle['p2']['trainer']][2]+=1
			for system in systems:
				scores['p1'][system],scores['p2'][system]=ladderRatingSystem[system].update({'p1':scores['p1'][system],'p2':scores['p2'][system]},ratings,winner)

			for player in ['p1','p2']:
				opp={'p1':'p2','p2':'p1'}
				if not ladderError:
					ladder[battle[player]['trainer']]['rating']=ratings[player]
				ladder[battle[player]['trainer']]['scores']=scores[player]
				trajectories[battle[player]['trainer']].append({'player':{'rating':ratings[player],'scores':scores[player]},'opponent':{'rating':ratings[opp[player]],'scores':scores[opp[player]]}})
				if 'outcome' in battle[player].keys():
					trajectories[battle[player]['trainer']][-1]['outcome']=battle[player]['outcome']
				else:
					trajectories[battle[player]['trainer']][-1]['outcome']='tie'
	idx+=1
	

if trajectoriesSaveFile:			
	pickle.dump(trajectories,open(trajectoriesSaveFile,'w'))

printme='Username,nBattles,nWins,R,RD,rpR,rpRD,ACRE,GXE'
x=[]
for system in systems:
	printme+=','+system
	x.append(system)
print printme
for player in ladder.keys():
	r=ladder[player]['rating']['r']
	rd=ladder[player]['rating']['rd']
	rpr=ladder[player]['rating']['rpr']
	rprd=ladder[player]['rating']['rprd']
	gxe = round(10000 / (1 + pow(10.0,(((1500 - rpr)) * math.pi / math.sqrt(3 * pow(math.log(10.0),2.0) * pow(rprd,2.0) + 2500 * (64 * pow(math.pi,2.0) + 147 * pow(math.log(10.0),2))))))) / 100
	acre= rpr-1.4079126393*rprd
	printme=player+','+str(len(trajectories[player]))+','+str(wltCounts[player][0])+','+str(r)+','+str(rd)+','+str(rpr)+','+str(rprd)+','+str(acre)+','+str(gxe)
	for system in x: #probably could just do system in systems, but this is safer
		printme+=','+str(ladderRatingSystem[system].getSortable(ladder[player]['scores'][system]))
	print printme
