#!/usr/bin/python
# -*- coding: latin-1 -*-

#Antar's X-Act v1

from common import victoryChance

K=50

def newPlayer():
	return 1000

def update(ratings,outcome):

	GXE={}
	for p in ['p1','p2']:
		GXE[p]=victoryChance(ratings[p]['r'],ratings[p]['rd'],1500.0,350.0)

	if outcome == 1:
		ratings['p1']['ladderRating']=ratings['p1']['ladderRating']+K*GXE['p2']
		ratings['p2']['ladderRating']=ratings['p2']['ladderRating']-K*GXE['p2']
	elif outcome == 2:
		ratings['p1']['ladderRating']=ratings['p1']['ladderRating']-K*GXE['p1']
		ratings['p2']['ladderRating']=ratings['p2']['ladderRating']+K*GXE['p1']
	else:
		ratings['p1']['ladderRating']=ratings['p1']['ladderRating']+K*(GXE['p2']-GXE['p1'])/2
		ratings['p2']['ladderRating']=ratings['p2']['ladderRating']+K*(GXE['p1']-GXE['p2'])/2
	

def getSortable(ladderRating):
	return ladderRating
