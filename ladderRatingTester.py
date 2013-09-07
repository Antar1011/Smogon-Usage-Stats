#!/usr/bin/python
# -*- coding: latin-1 -*-

import sys
import gzip
import json
import math
import cPickle as pickle
try:
	ladderRatingSystem = __import__(sys.argv[1])
except:
	sys.stderr.write('Incorrect syntax.\n')
	sys.stderr.write('Correct usage:\n')
	sys.stderr.write('\tpython ladderRatingTester.py SYSTEM FILES... [-t TRAJECTORYFILE]\n')
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
			raw[i]=raw[i]+']'

	for line in raw:
		battles = json.loads(line)
		for battle in battles:
			ratings={}
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
				if battle[player]['trainer'] in ladder.keys():
					ratings[player]['ladderRating']=ladder[battle[player]['trainer']]['ladderRating']
				else:
					ratings[player]['ladderRating']=ladderRatingSystem.newPlayer()
					ladder[battle[player]['trainer']]={}
					ladder[battle[player]['trainer']]['r']=ladder[battle[player]['trainer']]['rpr']=1500.0
					ladder[battle[player]['trainer']]['rd']=ladder[battle[player]['trainer']]['rprd']=350.0
					trajectories[battle[player]['trainer']]=[]
					wltCounts[battle[player]['trainer']]=[0,0,0]

			if 'outcome' in battle['p1'].keys():
				if battle['p1']['outcome'] == 'win':
					winner=1
					wltCounts[battle['p1']['trainer']][0]=wltCounts[battle['p1']['trainer']][0]+1
					wltCounts[battle['p2']['trainer']][1]=wltCounts[battle['p2']['trainer']][1]+1
				elif battle['p1']['outcome'] == 'loss':
					winner=2
					wltCounts[battle['p2']['trainer']][0]=wltCounts[battle['p2']['trainer']][0]+1
					wltCounts[battle['p1']['trainer']][1]=wltCounts[battle['p1']['trainer']][1]+1
				else:
					wltCounts[battle['p1']['trainer']][2]=wltCounts[battle['p1']['trainer']][2]+1
					wltCounts[battle['p2']['trainer']][2]=wltCounts[battle['p2']['trainer']][2]+1		
			ladderRatingSystem.update(ratings,winner)

			for player in ['p1','p2']:
				opp={'p1':'p2','p2':'p1'}
				if not ladderError:
					ladder[battle[player]['trainer']]=ratings[player]
				else:	
					ladder[battle[player]['trainer']]['ladderRating']=ratings[player]['ladderRating']
				trajectories[battle[player]['trainer']].append({'rating':ratings[player],'opponent':ratings[opp[player]]})
				if 'outcome' in battle[player].keys():
					trajectories[battle[player]['trainer']][-1]['outcome']=battle[player]['outcome']
				else:
					trajectories[battle[player]['trainer']][-1]['outcome']='tie'
	idx=idx+1

if trajectoriesSaveFile:			
	pickle.dump(trajectories,open(trajectoriesSaveFile,'w'))

print 'Username,R,RD,rpR,rpRD,ACRE,GXE,ladderScore,nBattles,nWins'
for player in ladder.keys():
	r=ladder[player]['r']
	rd=ladder[player]['rd']
	rpr=ladder[player]['rpr']
	rprd=ladder[player]['rprd']
	gxe = round(10000 / (1 + pow(10.0,(((1500 - rpr)) * math.pi / math.sqrt(3 * pow(math.log(10.0),2.0) * pow(rprd,2.0) + 2500 * (64 * pow(math.pi,2.0) + 147 * pow(math.log(10.0),2))))))) / 100
	acre= rpr-1.4079126393*rprd
	ladderScore=ladderRatingSystem.getSortable(ladder[player]['ladderRating'])

	print player+','+str(r)+','+str(rd)+','+str(rpr)+','+str(rprd)+','+str(acre)+','+str(gxe)+','+str(ladderScore)+','+str(len(trajectories[player]))+','+str(wltCounts[player][0])
