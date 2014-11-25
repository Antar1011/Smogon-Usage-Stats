#!/usr/bin/python
# -*- coding: latin-1 -*-

#Antar's Vegas-Inspired Ladder

from common import victoryChance

K=50.0

def newPlayer():
	return 1000.0

def update(score,ratings,outcome):

	GXE={}
	for p in ['p1','p2']:
		GXE[p]=victoryChance(ratings[p]['r'],ratings[p]['rd'],1500.0,350.0)

	if outcome == 1:
		score['p1']+=K*GXE['p2']
		score['p2']-=K*GXE['p2']
	elif outcome == 2:
		score['p1']-=K*GXE['p1']
		score['p2']+=+K*GXE['p1']
	else:
		score['p1']+=K*(GXE['p2']-GXE['p1'])/2
		score['p2']+=K*(GXE['p1']-GXE['p2'])/2

	return score['p1'],score['p2']
	

def getSortable(ladderRating):
	return ladderRating
