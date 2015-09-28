#!/usr/bin/python
#File I/O is going to be the main bottleneck. Doing moveset counting in batch (a folder at a time, rather than log by log)
#should be much more efficient, as keylookup.pickle need only be loaded once per run.

import string
import sys
import math
import cPickle as pickle
import json
import gzip
import os
import math

from common import keyify,weighting,readTable,aliases,victoryChance
from TA import nmod,statFormula,baseStats

def movesetCounter(filename, cutoff, teamtype, usage):
	file = gzip.open(filename,'rb')
	raw = file.read()
	file.close()

	raw=raw.split('][')
	for i in range(len(raw)):
		if (i>0):
			raw[i]='['+raw[i]
		if (i<len(raw)-1):
			raw[i]=raw[i]+']'

	species = keyLookup[filename[string.rfind(filename,'/')+1:]]
	for alias in aliases:
		if species in aliases[alias]:
			species = alias
			break

	bias = []
	stalliness = []
	abilities = {}
	items = {}
	happinesses = {}
	spreads = {}
	moves = {}
	movesets = []
	weights = []
	rawCount = 0
	gxes={}
	
	for line in raw:
		movesets = json.loads(line)
		for moveset in movesets:
			if teamtype:
				if teamtype not in moveset['tags']:
					continue
			rawCount = rawCount+1
			weight=weighting(1500.0,130.0,cutoff)
			if 'rating' in moveset.keys():
				if 'rpr' in moveset['rating'].keys() and 'rprd' in moveset['rating'].keys():
					gxe = victoryChance(moveset['rating']['rpr'],moveset['rating']['rprd'],1500.0,130.0)
					gxe=int(round(100*gxe))

					addMe=True
					if moveset['trainer'] in gxes:
						if gxes[moveset['trainer']] > gxe:
							addMe = False
					if addMe:
						gxes[moveset['trainer']]=gxe

					if moveset['rating']['rprd'] != 0.0:
						weight=weighting(moveset['rating']['rpr'],moveset['rating']['rprd'],cutoff)
						weights.append(weight)
			elif 'outcome' in moveset.keys():
				if moveset['outcome'] == 'win':
					weight=weighting(1540.16061434,122.858308077,cutoff)
				elif moveset['outcome'] == 'loss':
					weight=weighting(1459.83938566,122.858308077,cutoff)
				#else it's a tie, and we use 1500
			if moveset['ability'] not in keyLookup:
				moveset['ability'] = 'illuminate'
			if moveset['ability'] not in abilities:
				abilities[moveset['ability']] = 0.0
			abilities[moveset['ability']] = abilities[moveset['ability']] + weight

			if moveset['item'] not in keyLookup:
				moveset['item'] = 'nothing'
			if moveset['item'] not in items:
				items[moveset['item']] = 0.0
			items[moveset['item']] = items[moveset['item']] + weight

			if moveset['nature'] in ['serious','docile','quirky','bashful'] or moveset['nature'] not in keyLookup:
				nature = 'hardy'
		
			#round the EVs
			for stat in moveset['evs'].keys():
				ev=moveset['evs'][stat]
				if species == 'shedinja' and stat == 'hp':
					stat = 1
					moveset['evs']['stat']=0
					continue
			
				if stat == 'hp':
					n=-1
				else:
					n=nmod[moveset['nature']][{'atk': 0, 'def': 1, 'spa': 2, 'spd': 3, 'spe': 4}[stat]]
				x = statFormula(baseStats[keyify(species)][stat],moveset['level'],n,moveset['ivs'][stat],ev)

				while ev > 0:
					if x != statFormula(baseStats[keyify(species)][stat],moveset['level'],n,moveset['ivs'][stat],ev-1):
						break
					ev = ev-1
			
			moveset['evs'][stat]=ev

			spread = keyLookup[moveset['nature']]+':'
			for stat in ['hp','atk','def','spa','spd']:
				spread=spread+str(moveset['evs'][stat])+'/'
			spread=spread+str(moveset['evs']['spe'])
			if spread not in spreads:
				spreads[spread] = 0.0
			spreads[spread] += weight

			for move in moveset['moves']:
				if move in keyLookup:
					#I think it's valid to triple-count 'nothing' right now
					#if keyLookup[move]=='Nothing':
					#	continue
					if move not in moves:
						moves[move] = 0.0
					moves[move] += weight

			happiness = moveset['happiness']
			if happiness not in happinesses.keys():
				happinesses[happiness]=0.0
			happinesses[happiness]+=weight

	count = sum(abilities.values())
	gxes=list(reversed(sorted(gxes.values())))

	#teammate stats
	try:
		teammates = teammateMatrix[species]
	except KeyError:
		sys.stderr.write('No teammates data for '+filename+' ('+str(cutoff)+')\n')
		teammates={}
	for s in teammates:
		if s not in usage.keys():
			teammates[s]=0.0
		else:
			teammates[s]=teammates[s]-(count*usage[s])

	#checks and counters
	cc={}
	if species in encounterMatrix.keys():
		for s in encounterMatrix[species].keys():
			matchup = encounterMatrix[species][s]
			#number of times species is KOed by s + number of times species switches out against s over number of times
			#either (or both) is switched out or KOed (don't count u-turn KOs or force-outs)
			n=sum(matchup[0:6])
			if n>20:
				p=float(matchup[0]+matchup[3])/n
				d=math.sqrt(p*(1.0-p)/n)
				#cc[s]=p-4*d #using a CRE-style calculation
				cc[s]=[n,p,d]

	maxGXE = [0,0,0,0]
	if len(gxes) > 0:
		maxGXE = [len(gxes),gxes[0],gxes[int(math.ceil(0.01*len(gxes)))-1],gxes[int(math.ceil(0.20*len(gxes)))-1]]

	stuff = {
		'Raw count': rawCount,
		'Viability Ceiling': maxGXE,
		'Abilities': abilities,
		'Items': items,
		'Spreads': spreads,
		'Moves': moves,
		'Happiness' : happinesses,
		'Teammates': teammates,
		'Checks and Counters': cc}

	#print tables
	tablewidth = 40

	separator = ' +'
	for i in range(tablewidth):
		separator = separator + '-'
	separator = separator + '+ '
	print separator

	line = ' | '+species
	for i in range(len(species),tablewidth-1):
		line = line + ' '
	line = line + '| '
	print line

	print separator

	line = ' | Raw count: %d'%(rawCount)
	while len(line) < tablewidth+2:
		line = line + ' '
	line = line + '| '
	print line
	line = ' | Avg. weight: '
	if len(weights)>0:
		line = line+str(sum(weights)/len(weights))
	else:
		line = line+'---'
	while len(line) < tablewidth+2:
		line = line + ' '
	line = line + '| '
	print line
	line = ' | Viability Ceiling: %d'%(maxGXE[1])
	while len(line) < tablewidth+2:
		line = line + ' '
	line = line + '| '
	print line

	print separator

	for x in ['Abilities','Items','Spreads','Moves','Teammates','Checks and Counters']:
		table = []
		line = ' | '+x
		while len(line) < tablewidth+2:
			line = line + ' '
		line = line + '| '
		print line

		for i in stuff[x]:
			if (x in ['Spreads', 'Teammates','Checks and Counters']):
				table.append([i,stuff[x][i]])
			else:
				table.append([keyLookup[i],stuff[x][i]])
		if x is 'Checks and Counters':
			table=sorted(table, key=lambda table:-(table[1][1]-4.0*table[1][2]))
		else:
			table=sorted(table, key=lambda table:-table[1])
		total = 0.0
		for i in range(len(table)): 
			if (total > .95 and x is not 'Abilities') or (x is 'Abilities' and i>5) or (x is 'Spreads' and i>5) or (x is 'Teammates' and i>11) or (x is 'Checks and Counters' and i>11):
				if x is 'Moves':
					line = ' | %s %6.3f%%' % ('Other',400.0*(1.0-total))
				elif x not in ['Teammates','Checks and Counters']:
					line = ' | %s %6.3f%%' % ('Other',100.0*(1.0-total))
			else:
				if x is 'Checks and Counters':
					matchup = encounterMatrix[species][table[i][0]]
					n=sum(matchup[0:6])
					score=float(table[i][1][1])-4.0*table[i][1][2]
					if score < 0.5:
						break
					
					line = u' | %s %6.3f (%3.2f\u00b1%3.2f)' % (table[i][0],100.0*score,100.0*table[i][1][1],100*table[i][1][2])
					while len(line) < tablewidth+1:
						line = line + ' '
					line=line+' |\n |\t (%2.1f%% KOed / %2.1f%% switched out)' %(float(100.0*matchup[0])/n,float(100.0*matchup[3])/n)
					if float(100.0*matchup[0])/n < 10.0:
						line = line+' '
					if float(100.0*matchup[3])/n < 10.0:
						line = line+' '
				elif x is 'Teammates':
					line = ' | %s %+6.3f%%' % (table[i][0],100.0*table[i][1]/count)
					if table[i][1] < 0.005*count:
						break
				else:
					line = ' | %s %6.3f%%' % (table[i][0],100.0*table[i][1]/count)
			while len(line) < tablewidth+2:
				line = line + ' '
			line = line + '| '
			print line.encode('utf8')
			if (total > .95 and x is not 'Abilities') or (x is 'Abilities' and i>5) or (x is 'Spreads' and i>5) or (x is 'Teammates' and i>10) or (x is 'Checks and Counters' and i>10):
				break
			if x is 'Moves':
				total = total + float(table[i][1])/count/4.0
			elif x is 'Teammates':
				total = total + float(table[i][1])/count/5.0
			elif x is not 'Checks and Counters':
				total = total + float(table[i][1])/count
		print separator
	return stuff

file = open('keylookup.pickle')
keyLookup = pickle.load(file)
file.close()
keyLookup['nothing']='Nothing'
keyLookup['']='Nothing'

cutoff = 1500
cutoffdeviation = 0
teamtype = None

if (len(sys.argv) > 2):
	cutoff = float(sys.argv[2])
	if (len(sys.argv) > 3):
		teamtype = keyify(sys.argv[3])

specs = '-'
if teamtype:
	specs += teamtype+'-'
specs += '{:.0f}'.format(cutoff)

file = open('Raw/moveset/'+str(sys.argv[1])+'/teammate'+specs+'.pickle')
teammateMatrix = pickle.load(file)
file.close()

file = open('Raw/moveset/'+str(sys.argv[1])+'/encounterMatrix'+specs+'.pickle')
encounterMatrix = pickle.load(file)
file.close()

filename = 'Stats/'+str(sys.argv[1])+specs+'.txt'
file = open(filename)
table=file.readlines()
file.close()

usage,nBattles = readTable('Stats/'+str(sys.argv[1])+specs+'.txt')

pokes = []
for poke in usage.keys():
	pokes.append([poke,usage[poke]])
if sys.argv[1] in ['randombattle','challengecup','challengecup1v1','seasonal']:
	pokes=sorted(pokes)
else:
	pokes=sorted(pokes, key=lambda pokes:-pokes[1])

chaos = {'info': {'metagame': str(sys.argv[1]), 'cutoff': cutoff, 'cutoff deviation': cutoffdeviation, 'team type': teamtype, 'number of battles': nBattles},'data':{}}
for poke in pokes:
	if poke[1] < 0.0001: #1/100th of a percent
		break
	stuff = movesetCounter('Raw/moveset/'+str(sys.argv[1])+'/'+keyify(poke[0]),cutoff,teamtype,usage)
	stuff['usage']=poke[1]
	chaos['data'][poke[0]]=stuff


filename="Stats/chaos/"+str(sys.argv[1])+specs+".json"
d = os.path.dirname(filename)
if not os.path.exists(d):
	os.makedirs(d)
file=open(filename,'w')
file.write(json.dumps(chaos))
file.close()	
