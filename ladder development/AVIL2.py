#!/usr/bin/python
# -*- coding: latin-1 -*-

#Antar's Vegas-Inspired Ladder v2

from common import victoryChance

K=50.0

def newPlayer():
	return 1000.0

def update(score,ratings,outcome):

	GXE={}
	for p in ['p1','p2']:
		GXE[p]=victoryChance(ratings[p]['r'],ratings[p]['rd'],1500.0,350.0)

	pointChange=K*GXE['p1']+GXE['p2']/2

	if outcome == 1:
		score['p1']+=pointChange
		score['p2']-=pointChange
	elif outcome == 2:
		score['p1']-=pointChange
		score['p2']+=pointChange
	#else: no change
	
	return score['p1'],score['p2']
	

def getSortable(ladderRating):
	return ladderRating
