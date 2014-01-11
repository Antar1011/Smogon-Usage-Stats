#!/usr/bin/python
# -*- coding: latin-1 -*-

#vanilla Elo

from common import victoryChance

K=25.0

def newPlayer():
	return 1000.0

def update(p1rating,p2rating,outcome):
	S={}
	outcome=int(outcome)
	if outcome == 1:
		S['p1']=1.0
	elif outcome == 2:
		S['p1']=0.0
	else: #if outcome == 0
		S['p1']=0.5
	S['p2']=1.0-S['p1']

	E={}
	E['p1']=victoryChance(p1rating,0.0,p2rating,0.0)
	E['p2']=1.0-E['p1']

	p1rating+=K*(S['p1']-E['p1'])
	p2rating+=K*(S['p2']-E['p2'])
	return p1rating,p2rating,E['p1']

def newRatingPeriod(rating):
	return rating

def headers():
	return 'Elo R'
def printRating(rating):
	return str(rating)
