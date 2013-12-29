#!/usr/bin/python
# -*- coding: latin-1 -*-

#Converging Order-Invariant Ladder

from common import victoryChance
import math

def newPlayer():
	return [0,0]

def update(score,ratings,outcome):

	GXE={}
	for p in ['p1','p2']:
		GXE[p]=victoryChance(ratings[p]['r'],ratings[p]['rd'],1500.0,350.0)

	if outcome == 1:
		score['p1'][0]+=GXE['p2']
		score['p2'][1]+=(1.0-GXE['p1'])
	elif outcome == 2:
		score['p2'][0]+=GXE['p1']
		score['p1'][1]+=(1.0-GXE['p2'])
	#else: no change
	
	return score['p1'],score['p2']
	

def getSortable(ladderRating):
	if ladderRating[0] == 0:
		return 0
	N=sum(ladderRating)
	w=float(ladderRating[0])/N
	return 4000*w*math.pow(2,-50.0/ladderRating[0])
