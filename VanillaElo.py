#!/usr/bin/python
# -*- coding: latin-1 -*-

#vanilla Elo

from common import victoryChance

K=50.0

def newPlayer():
	return 1000.0

def update(score,ratings,outcome):
	S={}
	if outcome == 1:
		S['p1']=1
	elif outcome == 2:
		S['p1']=0
	else: #if outcome == 0
		S['p1']=0.5
	S['p2']=1.0-S['p1']

	E={}
	E['p1']=victoryChance(score['p1'],0.0,score['p2'],0.0)
	E['p2']=1.0-E['p1']

	if (E['p1'] > E['p2']):
		open("elo-validator.txt",'a').write(str(E['p1'])+','+str(S['p1'])+'\n')
	else:
		open("elo-validator.txt",'a').write(str(E['p2'])+','+str(S['p2'])+'\n')

	for p in ['p1','p2']:
		score[p]+=K*(S[p]-E[p])

	return score['p1'],score['p2']

def getSortable(ladderRating):
	return ladderRating
