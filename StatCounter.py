#!/usr/bin/python
# -*- coding: latin-1 -*-
#Loads an intermediate battle summary file created by LogReader and compiles usage and metagame stats, which
#are written to the appropriate folders. Also, if the user so wants, the script will generate a "matchup matrix"
#which looks at what happens when Pokemon X meets up with Pokemon Y. This could conceivably be used to come up
#with a statistical list of best checks and counters for each Pokemon, but I haven't yet made that script.

#encounterMatrix key: for entries encounterMatrix[poke1][poke2][i], i=...
#0: poke1 was KOed
#1: poke2 was KOed
#2: double down
#3: poke1 was switched out
#4: poke2 was switched out
#5: double switch
#6: poke1 was forced out
#7: poke2 was forced out
#8: poke1 was u-turn KOed
#9: poke2 was u-turn KOed
#10: poke1 was foddered
#11: poke2 was foddered
#12: no clue what happened

import string
import sys
import math
import cPickle as pickle
import os
import json
import lzma

from common import *

#this is a lookup table for the outcomes if poke1 and poke2 were exchanged
otherGuy = [1,0,2,4,3,5,7,6,9,8,11,10,12]

cutoff = 1500 #this is our default, but we can change it for '1337' stats
cutoffdeviation = 0 #nonzero for '1337' stats

if (len(sys.argv) > 2):
	cutoff = float(sys.argv[2])

tier = str(sys.argv[1])

specs = ''
if cutoff != 1500:
	specs = '-'+str(cutoff)

filename="Raw/"+tier#+".txt"
file = open(filename,'rb')
raw = file.read()
file.close()

raw=raw.split('\xfd7zXZ')
for i in range(len(raw)):
	raw[i]='\xfd7zXZ'+raw[i]
raw = raw[1:]

filename="Stats/"+tier+specs+".txt"
d = os.path.dirname(filename)
if not os.path.exists(d):
	os.makedirs(d)
usagefile=open(filename,'w')
filename="Stats/metagame/"+tier+specs+".txt"
d = os.path.dirname(filename)
if not os.path.exists(d):
	os.makedirs(d)
if tier != "1v1":
	metagamefile=open(filename,'w')
filename="Raw/moveset/"+tier+"/teammate"+specs+".pickle"
teammatefile=open(filename,'w')
filename="Raw/moveset/"+tier+"/encounterMatrix"+specs+".pickle"
encounterfile=open(filename,'w')


battleCount = 0
teamCount = 0
counter = {'raw': {}, 'real': {}, 'weighted': {}}
leadCounter = {'raw': {}, 'weighted': {}}
#We're not doing these right now
#turnCounter = {}
#KOcounter = {}
#TCsquared = {} #for calculating std. dev
#KCsquared = {} #	"
encounterMatrix = {}
teammateMatrix = {}
tagCounter = {}
stallCounter = []
ratingCounter = []
weightCounter = []
WLratings = {'win':[],'loss':[]}

for line in raw:
	#print line
	battles = json.loads(lzma.decompress(line))

	for battle in battles:

		weight={}

		for player in ['p1','p2']:
			team = []
			if 'rating' in battle[player].keys():
				if 'rpr' in battle[player]['rating'].keys() and 'rprd' in battle[player]['rating'].keys():
					if battle[player]['rating']['rprd'] != 0.0:
						weight[player] = weighting(battle[player]['rating']['rpr'],battle[player]['rating']['rprd'],cutoff)
						ratingCounter.append(battle[player]['rating'])
				
						if 'outcome' in battle[player].keys():
							WLratings[battle[player]['outcome']].append([battle[player]['rating']['rpr'],battle[player]['rating']['rprd'],weight[player]])
				
			if player not in weight.keys(): #if there's a ladder error, we have no idea what the player's rating is, so treat like a new player
				weight[player] = weighting(1500,350.0,cutoff)

				#try using outcome
				if 'outcome' in battle[player].keys():
					if battle[player]['outcome'] == 'win':
						weight[player] = weighting(1662.3108925672,290.31896252483,cutoff)
					elif battle[player]['outcome'] == 'loss':
						weight[player] = weighting(1337.6891074328,290.31896252483,cutoff)

			weightCounter.append(weight[player])

			for poke in battle[player]['team']:
				#annoying alias shit
				species = poke['species']
				for alias in aliases:
					if species in aliases[alias]:
						species = alias
						break

				team.append(species)

				#if species not already in the tables, you gotta add them
				if species not in counter['raw'].keys():
					counter['raw'][species]=0.0
					counter['real'][species]=0.0
					counter['weighted'][species]=0.0
			
				#count usage
				counter['raw'][species]=counter['raw'][species]+1.0
				if poke['turnsOut'] > 0:
					counter['real'][species]=counter['real'][species]+1.0
				counter['weighted'][species]=counter['weighted'][species]+weight[player]

				#count metagame stuff
				for tag in battle[player]['tags']:
					if tag not in tagCounter.keys():
						tagCounter[tag] = 0.0
					tagCounter[tag] = tagCounter[tag]+weight[player] #metagame stuff is weighted
				stallCounter.append([battle[player]['stalliness'],weight[player]])

			teamCount = teamCount + 1

			#teammate stats
			for i in range(len(team)):
				for j in range(i):
					if team[i] not in teammateMatrix.keys():
						teammateMatrix[team[i]]={}
					if team[j] not in teammateMatrix.keys():
						teammateMatrix[team[j]]={}
					if team[j] not in teammateMatrix[team[i]].keys():
						teammateMatrix[team[i]][team[j]]=0.0
					teammateMatrix[team[i]][team[j]]=teammateMatrix[team[i]][team[j]]+weight[player] #teammate stats are weighted
					teammateMatrix[team[j]][team[i]]=teammateMatrix[team[i]][team[j]] #nice symmetric matrix

		if tier not in ['doublesvgc2013dev','doublesvgc2013','smogondoubles','1v1']: #lead stats for doubles is not currently supported
			#lead stats
			leads=['empty','empty']
			if len(battle['matchups'])==0:
				#this happens if the player forfeits after six turns and no switches--rare but possible
				for i in range(2):
					for poke in battle[['p1','p2'][i]]['team']:
						if poke['turnsOut'] > 0:
							leads[i] = poke['species']
							break
			else:
				for i in range(2):
					#it is utterly imperative that the p1 lead is first and the p2 lead second
					leads[i] = battle['matchups'][0][i]

			if 'empty' in leads:
				print "Something went wrong."
				print battle

			for i in range(2):
				species = leads[i]
				#annoying alias shit
				for alias in aliases:
					if species in aliases[alias]:
						species = alias
						break
				if species not in leadCounter['raw'].keys():
					leadCounter['raw'][species]=0.0
					leadCounter['weighted'][species]=0.0

				leadCounter['raw'][species]=leadCounter['raw'][species]+1.0
				leadCounter['weighted'][species]=leadCounter['weighted'][species]+weight[['p1','p2'][i]]

		#encounter Matrix
		w=min(weight.values())
		for matchup in battle['matchups']:
			if matchup[0] not in encounterMatrix.keys():
				encounterMatrix[matchup[0]]={}
			if matchup[1] not in encounterMatrix.keys():
				encounterMatrix[matchup[1]]={}
			if matchup[1] not in encounterMatrix[matchup[0]].keys():
				encounterMatrix[matchup[0]][matchup[1]]=[0 for k in range(13)]
				encounterMatrix[matchup[1]][matchup[0]]=[0 for k in range(13)]
			encounterMatrix[matchup[0]][matchup[1]][matchup[2]]=encounterMatrix[matchup[0]][matchup[1]][matchup[2]]+w #encounter Matrix is weighed
			encounterMatrix[matchup[1]][matchup[0]][otherGuy[matchup[2]]]=encounterMatrix[matchup[1]][matchup[0]][otherGuy[matchup[2]]]+w #by the inferior player

		battleCount = battleCount + 1
	

total={}
for i in ['raw','real','weighted']:
	total[i] = sum(counter[i].values())

pokedict = {}
for i in counter['raw'].keys():
	pokedict[i]=[counter['raw'][i],counter['real'][i],counter['weighted'][i]]

if 'empty' in pokedict.keys(): #delete no-entry slot
		del pokedict['empty']

pokes = []
for i in pokedict:
	pokes.append([i]+pokedict[i])


#write teammates and encounter matrix to file
pickle.dump(teammateMatrix,teammatefile)
teammatefile.close()
pickle.dump(encounterMatrix,encounterfile)
encounterfile.close()

#sort by weighted usage
if tier in ['challengecup1v1','1v1']:
	pokes=sorted(pokes, key=lambda pokes:-pokes[2])
else:
	pokes=sorted(pokes, key=lambda pokes:-pokes[3])
p=[]
usagefile.write(" Total battles: "+str(battleCount)+"\n")
usagefile.write(" Avg. weight/team: "+str(round(total['weighted']/battleCount/12,3))+"\n")
usagefile.write(" + ---- + ------------------ + --------- + ------ + ------- + ------ + ------- + \n")
usagefile.write(" | Rank | Pokemon            | Usage %   | Raw    | %       | Real   | %       | \n")
usagefile.write(" + ---- + ------------------ + --------- + ------ + ------- + ------ + ------- + \n")
for i in range(0,len(pokes)):
	if pokes[i][1] == 0:
		break
	usagefile.write(' | %-4d | %-18s | %8.5f%% | %-6d | %6.3f%% | %-6d | %6.3f%% | \n' % (i+1,pokes[i][0],100.0*pokes[i][3]/total['weighted']*6.0,pokes[i][1],100.0*pokes[i][1]/total['raw']*6.0,pokes[i][2],100.0*pokes[i][2]/max(total['real'],1.0)*6.0))
	p.append(pokes[i])
usagefile.write(" + ---- + ------------------ + --------- + ------ + ------- + ------ + ------- + \n")
usagefile.close()

if tier not in ['doublesvgc2013dev','doublesvgc2013','smogondoubles','1v1']: #lead stats for doubles is not currently supported
	#lead analysis

	filename="Stats/leads/"+tier+specs+".txt"
	d = os.path.dirname(filename)
	if not os.path.exists(d):
		os.makedirs(d)
	leadsfile=open(filename,'w')

	pokedict = {}
	for i in leadCounter['raw'].keys():
		pokedict[i]=[leadCounter['raw'][i],leadCounter['weighted'][i]]
	if 'empty' in pokedict.keys(): #delete no-entry slot
			del pokedict['empty']
	pokes = []
	for i in pokedict:
		pokes.append([i]+pokedict[i])
	pokes=sorted(pokes, key=lambda pokes:-pokes[2])
	leadsfile.write(" Total leads: "+str(battleCount*2)+"\n")
	leadsfile.write(" + ---- + ------------------ + --------- + ------ + ------- + \n")
	leadsfile.write(" | Rank | Pokemon            | Usage %   | Raw    | %       | \n")
	leadsfile.write(" + ---- + ------------------ + --------- + ------ + ------- + \n")
	for i in range(0,len(pokes)):
		if pokes[i][1] == 0:
			break
		leadsfile.write(" | %-4d | %-18s | %8.5f%% | %-6d | %6.3f%% | \n" % (i+1,pokes[i][0],100.0*pokes[i][2]/sum(leadCounter['weighted'].values()),pokes[i][1],100.0*pokes[i][1]/sum(leadCounter['raw'].values())))
	leadsfile.write(" + ---- + ------------------ + --------- + ------ + ------- + \n")
	leadsfile.close()

#metagame analysis
if tier != "1v1":
	tags = []
	for tag in tagCounter:
		tags.append([tag,tagCounter[tag]])
	tags=sorted(tags, key=lambda tags:-tags[1])

	for i in range(0,len(tags)):
		line = ' '+tags[i][0]
		for j in range(len(tags[i][0]),30):
			line = line + '.'
		line = line + '%8.5f%%' % (100.0*tags[i][1]/total['weighted'])
		metagamefile.write(line+'\n')
	metagamefile.write('\n')

	#stalliness
	stallCounter=sorted(stallCounter, key=lambda stallCounter:stallCounter[0])

	#figure out a good bin range by looking at .1% and 99.9% points
	low = stallCounter[len(stallCounter)/1000][0]
	high = stallCounter[len(stallCounter)-len(stallCounter)/1000-1][0]

	nbins = 13 #this is actually only a rough idea--I think it might be the minimum?

	if (low > 0):
		low = 0.0
	elif (high < 0):
		high = 0.0

	binSize = (high-low)/(nbins-1)
	#this is bound to be an ugly number, so let's make it pretty
	for x in [10,5,2.5,2,1.5,1,0.5,0.25,0.2,0.1,0.05]:
		if binSize > x:
			break
	#if binSize < 0.05, fuck it--I'm not zooming in any further
	binSize = x
	histogram = [[0.0,0]]
	x=binSize
	while x+binSize/2 < high:
		histogram.append([x,0])
		x=x+binSize
	x=-binSize
	while x-binSize/2 > low:
		histogram.append([x,0])
		x=x-binSize
	histogram=sorted(histogram, key=lambda histogram:histogram[0])
	nbins = len(histogram)

	for start in range(len(stallCounter)):
		if stallCounter[start] >= histogram[0][0]-binSize/2:
			break

	j=0
	for i in range(start,len(stallCounter)):
		while stallCounter[i][0] > histogram[0][0]+binSize*(j+0.5):
			j=j+1
		if j>=len(histogram):
			break
		histogram[j][1] = histogram[j][1]+stallCounter[i][1]

	maximum = 0
	for i in range(len(histogram)):
		if histogram[i][1] > maximum:
			maximum = histogram[i][1]

	nblocks = 30 #maximum number of blocks to go across
	blockSize = maximum/nblocks

	if blockSize > 0:
		x=0.0
		y=0.0
		for score in stallCounter:
			x=x+score[0]*score[1]
			y=y+score[1]	

		#print histogram
		metagamefile.write(' Stalliness (mean: %6.3f)\n'%(x/y))
		for i in range(len(histogram)):
			if histogram[i][0]%(2.0*binSize) < binSize/2:
				line = ' '
				if histogram[i][0]>0.0:
					line=line+'+'
				elif histogram[i][0] == 0.0:
					line=line+' '
				line = line+'%3.1f|'%(histogram[i][0])
			else:
				line = '     |'
			for j in range(int((histogram[i][1]+blockSize/2)/blockSize)):#poor man's rounding
				line = line + '#'
			metagamefile.write(line+'\n')
		metagamefile.write(' more negative = more offensive, more positive = more stall\n')
		metagamefile.write(' one # = %5.2f%%\n'%(100.0*blockSize/y))

	metagamefile.close()
#outfile=open('stall.dat','w')
#for line in metricCounter:
#	for item in line:
#		outfile.write(str(item)+'\t')
#	outfile.write('\n')
#outfile.close()
#filename="Stats/rating/"+tier+".txt"
#d = os.path.dirname(filename)
#if not os.path.exists(d):
#	os.makedirs(d)
#outfile=open(filename,'w')
#scores=['r','rd','rpr','rprd']
#for score in scores:
#	outfile.write(score+'\t')
#outfile.write('\n')
#for rating in ratingCounter:
#	for score in scores:
#		outfile.write(str(rating[score])+'\t')
#	outfile.write('\n')
#outfile.close()

#filename="Stats/weighting/"+tier+specs+".txt"
#d = os.path.dirname(filename)
#if not os.path.exists(d):
#	os.makedirs(d)
#outfile=open(filename,'w')
#for line in weightCounter:
#	outfile.write(str(line)+'\n')
#outfile.close()

#for outcome in ['win','loss']:
#	filename="Stats/wl/"+tier+specs+outcome+".txt"
#	d = os.path.dirname(filename)
#	if not os.path.exists(d):
#		os.makedirs(d)
#	outfile=open(filename,'w')
#	for line in WLratings[outcome]:
#		outfile.write('\t'.join([str(i) for i in line])+'\n')
#	outfile.close()

