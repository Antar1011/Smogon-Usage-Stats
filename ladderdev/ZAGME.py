#!/usr/bin/python
# -*- coding: latin-1 -*-

#Zarel and Antar's Glicko-Modified Elo

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
	E['p1']=victoryChance(ratings['p1']['r'],ratings['p1']['rd'],ratings['p2']['r'],ratings['p2']['rd'])
	E['p2']=1.0-E['p1']
	
	for p in ['p1','p2']:
		score[p]+=K*(S[p]-E[p])

	return score['p1'],score['p2']

def getSortable(ladderRating):
	return ladderRating
