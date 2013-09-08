#!/usr/bin/python
# -*- coding: latin-1 -*-

#Antar's Vegas-Inspired Ladder

from common import victoryChance

K=50.0

def newPlayer():
	return 1000.0

def update(scores,ratings,outcome):

	GXE={}
	for p in ['p1','p2']:
		GXE[p]=victoryChance(ratings[p]['r'],ratings[p]['rd'],1500.0,350.0)

	if outcome == 1:
		scores['p1']+=K*GXE['p2']
		scores['p2']-=K*GXE['p2']
	elif outcome == 2:
		scores['p1']-=-K*GXE['p1']
		scores['p2']+=+K*GXE['p1']
	else:
		scores['p1']+=K*(GXE['p2']-GXE['p1'])/2
		scores['p2']+=K*(GXE['p1']-GXE['p2'])/2

	return scores['p1'],scores['p2']
	

def getSortable(ladderRating):
	return ladderRating
