#!/usr/bin/python
# -*- coding: latin-1 -*-
#File I/O is going to be the main bottleneck. Doing log reading in batch (a folder at a time, rather than log by log)
#should be much more efficient, as TA.py and the files it requires need only be loaded once per run.

import sys
import json
import os

def LogReader(filename):
	try:
		log = json.loads(open(filename).readline())
	except ValueError:
		sys.stderr.write(filename+' is not a valid log.\n')
		return False

	whowon = 0 #0 for tie/unknown, 1 for p1, 2 for p2
	if 'log' not in log.keys():
		return False
	#if log['endType'] != 'normal':
	#	return False

	#if '|tie' in log['log']:
	#	whowon = 0
	if '|win|'+log['p1'] in log['log']:
		whowon = 1
	if '|win|'+log['p2'] in log['log']:
		if whowon == 1:
			sys.stderr.write(filename+'\n')
			sys.stderr.write('This battle had two winners.\n')
			return False
		else:
			whowon = 2
	if log['endType'] not in ['normal','forfeit']:
		sys.err.write(log['endType']+'\n')
	return log['p1'],log['p2'],hash(str(log['p1team'])),hash(str(log['p2team'])),whowon,log['endType'],log['turns']

for folder in sorted(os.listdir(sys.argv[1])):
	for filename in sorted(os.listdir(sys.argv[1]+folder)):
		try:
			p1,p2,team1,team2,whowon,endType,turns=LogReader(sys.argv[1]+folder+'/'+filename)
		except:
			continue
		print folder+','+p1.encode('utf-8')+','+str(team1)+','+p2.encode('utf-8')+','+str(team2)+','+str(whowon)+','+endType.encode('utf-8')+','+str(turns)
