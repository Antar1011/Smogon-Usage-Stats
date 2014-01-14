#!/usr/bin/python
# -*- coding: latin-1 -*-

#Glicko-2

import math
from common import victoryChance

def g(phi):
		return pow(1.0+3.0*phi*phi/math.pi/math.pi,-0.5)
def expectedScore(R1,R2,RD2):
		return 1.0/(1.0+math.exp(-g(phi(RD2))*(mu(R1)-mu(R2))))
def mu(R):
		return (R-1500.0)/173.7178
def phi(RD):
		return RD/173.7178

tau=0.2
sigma0=0.11
RDmax=100


def newPlayer():
	return {'R':1500.0,'RD':RDmax,'sigma':sigma0,'v':0.0,'Delta':0.0}

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
	E['p1']=expectedScore(p1rating['R'],p2rating['R'],p2rating['RD'])
	E['p2']=expectedScore(p2rating['R'],p1rating['R'],p1rating['RD'])

	p1rating['v'] += pow(g(phi(p2rating['RD'])),2)*E['p1']*E['p2']
	p1rating['Delta'] += g(phi(p2rating['RD']))*(S['p1']-E['p1'])

	p2rating['v'] += pow(g(phi(p1rating['RD'])),2)*E['p2']*E['p1']
	p2rating['Delta'] += g(phi(p1rating['RD']))*(S['p2']-E['p2'])

	#return p1rating,p2rating,victoryChance(p1rating['R'],p1rating['RD'],p2rating['R'],p2rating['RD'])
	return p1rating,p2rating,E['p1']

def newRatingPeriod(rating):

	if rating['v'] == 0.0:
		if rating['Delta'] != 0:
			print 'WTF?'
			print rating['v'],rating['Delta']
		p=math.sqrt(pow(phi(rating['RD']),2)+pow(rating['sigma'],2))
		rating['RD']=173.7178*p
	else:
		v=1.0/rating['v']
		Delta=v*rating['Delta']
		p=phi(rating['RD'])

		a=2.0*math.log(rating['sigma'])
		def f(x):
			return math.exp(x)*(Delta*Delta-p*p-v-math.exp(x))/2.0/math.pow((p*p+v+math.exp(x)),2.0)-(x-a)/tau/tau
		def C(A,B,fA,fB):
			return A+(A-B)*fA/(fB-fA)

		A=a
		B=0
		if Delta*Delta > p*p+v:
			B=math.log(Delta*Delta-p*p-v)
		else:
			k=1
			while f(a-k*tau)<0:
				k+=1
			B=a-k*tau

		fA=f(A)
		fB=f(B)
		epsilon=0.000001
		while abs(B-A) > epsilon:
			c=C(A,B,fA,fB)
			fC=f(c)
			if fC*fB<0:
				A=B
				fA=fB
			else:
				fA=fA/2.0
			B=c
			fB=fC


		sigma=math.exp(A/2)
		p=math.pow(1.0/(p*p+sigma*sigma)+1.0/v,-0.5)
		m=mu(rating['R'])+p*p*Delta/v

		rating['R']=173.7178*m+1500
		rating['RD']=173.7178*p
	
	if rating['RD']>RDmax:
		rating['RD']=RDmax
	
	rating['v']=0
	rating['Delta']=0

	return rating

def headers():
	return 'Glicko2 R,Glicko2 RD'
def printRating(rating):
	return str(rating['R'])+','+str(rating['RD'])
