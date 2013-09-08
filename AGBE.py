#!/usr/bin/python
# -*- coding: latin-1 -*-

#Antar's GXE-Based Elo

from common import victoryChance

K=50.0

def newPlayer():
	return 1000.0

def update(scores,ratings,outcome):
	S={}
	if outcome == 1:
		S['p1']=1
	elif outcome == 2:
		S['p1']=0
	else: #if outcome == 0
		S['p1']=0.5
	S['p2']=1.0-S['p1']

	E={}
	E['p1']=victoryChance(1500.0,350.0,ratings['p2']['r'],ratings['p2']['rd'])
	E['p2']=victoryChance(1500.0,350.0,ratings['p1']['r'],ratings['p2']['rd'])
	
	for p in ['p1','p2']:
		scores[p]+=K*(S[p]-E[p])

	return scores['p1'],scores['p2']

def getSortable(ladderRating):
	return ladderRating
