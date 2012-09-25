#!/usr/bin/python
# -*- coding: latin-1 -*-

import string
import sys
import math
import cPickle as pickle

mostCommon = False #finding most common sets takes waay too long

nmod = {'hardy': [10,10,10,10,10],
	'lonely': [11,9,10,10,10],
	'brave': [11,10,9,10,10],
	'adamant': [11,10,10,9,10],
	'naughty': [11,10,10,10,9],
	'bold': [9,11,10,10,10],
	'docile': [10,10,10,10,10],
	'relaxed': [10,11,9,10,10],
	'impish': [10,11,10,9,10],
	'lax': [10,11,10,10,9],
	'timid': [9,10,11,10,10],
	'hasty': [10,9,11,10,10],
	'serious': [10,10,10,10,10],
	'jolly': [10,10,11,9,10],
	'naive': [10,10,11,10,9],
	'modest': [9,10,10,11,10],
	'mild': [10,9,10,11,10],
	'quiet': [10,10,9,11,10],
	'bashful': [10,10,10,10,10],
	'rash': [10,10,10,11,9],
	'calm': [9,10,10,10,11],
	'gentle': [10,9,10,10,11],
	'sassy': [10,10,9,10,11],
	'careful': [10,10,10,9,11],
	'quirky': [10,10,10,10,10]}

def keyify(s):
	sout = ''
	for c in s:
		if c in string.uppercase:
			sout = sout + c.lower()
		elif c in string.lowercase + '1234567890':
			sout = sout + c
	return sout

def compare(set1,set2):
	diff = 0
	if set1['ability'] != set2['ability']:
		diff = diff + 2
	#anything higher-order would be a PITA, since it should be done by species

	if set1['nature'] != set2['nature']:
		d = 0
		for i in range(5):
			d = d + abs(nmod[set1['nature']][i]-nmod[set2['nature']][i])*abs(nmod[set1['nature']][i]-nmod[set2['nature']][i])
		#modest and timid have a diff of 2
		#jolly and timid have a diff of 2--this is fine, because if they're really different, it'll be reflected in the EV spread
		#modest and relaxed have a diff of 4
		#modest and jolly have a diff of 6
		#modest and adamant have a diff of 8
		diff=diff+d/2 #divide by 2 because if you don't, it's a bit crazy
		


	for ev in set1['evs']:
		evtype = [0,0]
	#okay, so the idea here should be that stats either have:
	#	-no investment (0-8 EVs)
		if set1['evs'][ev] <= 8:
			evtype[0]=0
	#	-some investment
		elif set1['evs'][ev] <=64:
			evtype[0]=1
	#	-significant investment
		elif set1['evs'][ev] <=240:
			evtype[0]=2
	#	-max investment (244-252 EVs)
		else:
			evtype[0]=3
	#this is totally gonna crash & burn for LC

		if set2['evs'][ev] <= 8:
			evtype[1]=0
		elif set2['evs'][ev] <=64:
			evtype[1]=1
		elif set2['evs'][ev] <=240:
			evtype[1]=2
		else:
			evtype[1]=3

		diff=diff+abs(evtype[0]-evtype[1])

	diff = diff + 4 - len(set(set1['moves']).intersection(set2['moves']))
	#anything higher order is gonna be a pain--Flamethrower vs. Fire Blast, for instance

	return diff
	 
def movesetCounter(filename):
	file = open(filename)
	raw = file.readlines()
	file.close()
	species = keyLookup[filename[string.rfind(filename,'/')+1:string.rfind(filename,'.')]]

	bias = []
	stalliness = []
	abilities = {}
	items = {}
	natures = {}
	evspreads = {}
	moves = {}
	movesets = []
	count = 0

	for line in raw:
		count = count + 1
		moveset = line[:len(line)-1].split('\t')

		bias.append(float(moveset[0]))

		stalliness.append(float(moveset[1]))

		#level = moveset[2]

		ability = moveset[3]
		if ability not in abilities:
			abilities[ability] = 0.0
		abilities[ability] = abilities[ability] + 1.0

		item = moveset[4]
		if item not in keyLookup:
			item = 'nothing'
		if item not in items:
			items[item] = 0.0
		items[item] = items[item] + 1.0

		nature = moveset[5]
		if nature in ['serious','docile','quirky','bashful']:
			nature = 'hardy'
		if nature not in natures:
			natures[nature] = 0.0
		natures[nature] = natures[nature] + 1.0	

		#ivs = moveset[6:12]

		evs = moveset[12:18]
		for i in range(0,6): #round the EVs
			evs[i] = str(int(evs[i])/4*4)
		#to-do: Little Cup rounding
		evspread = '/'.join(evs)
		if evspread not in evspreads:
			evspreads[evspread] = 0.0
		evspreads[evspread] = evspreads[evspread] + 1.0

		move = moveset[18:len(moveset)-1]
		for i in range(len(move)):
			if move[i] in keyLookup:
				if move[i] not in moves:
					moves[move[i]] = 0.0
				moves[move[i]] = moves[move[i]]+1

		if mostCommon:
			moveset={
				'ability': ability,
				'item': item,
				'nature': nature,
				'evs': {
					'hp': evs[0],
					'atk': evs[1],
					'def': evs[2],
					'spa': evs[3],
					'spd': evs[4],
					'spe': evs[5]},
				'moves': move,
				'variations': [],
				'count': 1 }

			i=0
			match = False
			for i in range(len(movesets)):
				if compare(moveset,movesets[i]) == 0:
					movesets[i]['count'] = movesets[i]['count']+1
					match = True
					break
			if not match:
			movesets.append(moveset)

	stuff = {
		'Abilties': abilities,
		'Items': items,
		'Natures': natures,
		'EV spreads': evspreads,
		'Moves': moves}


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

	for x in ['Abilties','Items','Natures','EV spreads','Moves']:
		table = []
		line = ' | '+x
		while len(line) < tablewidth+2:
			line = line + ' '
		line = line + '| '
		print line

		for i in stuff[x]:
			if (x is 'EV spreads'):
				table.append([i,stuff[x][i]])
			else:
				table.append([keyLookup[i],stuff[x][i]])
		table=sorted(table, key=lambda table:-table[1])
		total = 0.0
		for i in range(len(table)): 
			if total > .95 or (x is 'EV spreads' and i>5):
				if x is 'Moves':
					line = ' | %s %6.3f%%' % ('Other',400.0*(1.0-total))
				else:
					line = ' | %s %6.3f%%' % ('Other',100.0*(1.0-total))
			else:
				line = ' | %s %6.3f%%' % (table[i][0],100.0*table[i][1]/count)
			while len(line) < tablewidth+2:
				line = line + ' '
			line = line + '| '
			print line
			if total > .95 or (x is 'EV spreads' and i>5):
				break
			if x is 'Moves':
				total = total + float(table[i][1])/count/4.0
			else:
				total = total + float(table[i][1])/count
		print separator
	
	#combine movesets to try to find most common ones
	if len(movesets) > 1 and mostCommon:
		#for now we just report the top two with no variations
		line = ' | Most common sets:'
		while len(line) < tablewidth+2:
			line = line + ' '
		line = line + '| '
		print line
		line = ' |'
		while len(line) < tablewidth+2:
			line = line + ' '
		line = line + '| '
		print line

		movesets=sorted(movesets, key=lambda movesets:-movesets['count'])
		for common in [movesets[0],movesets[1]]:
			line = ' | '+species+" @ "+keyLookup[common['item']]
			while len(line) < tablewidth+2:
				line = line + ' '
			line = line + '| '
			print line
			line = ' | Ability: '+keyLookup[common['ability']]
			while len(line) < tablewidth+2:
				line = line + ' '
			line = line + '| '
			print line
			line = ' | '+keyLookup[common['nature']]+" nature"
			while len(line) < tablewidth+2:
				line = line + ' '
			line = line + '| '
			print line
			line = ' | EVs: %s/%s/%s/%s/%s/%s'%(common['evs']['hp'],common['evs']['atk'],common['evs']['def'],common['evs']['spa'],common['evs']['spd'],common['evs']['spe'])
			while len(line) < tablewidth+2:
				line = line + ' '
			line = line + '| '
			print line
			for move in common['moves']:
				line =' |    -'+keyLookup[move]
				while len(line) < tablewidth+2:
					line = line + ' '
				line = line + '| '
				print line
		print separator
	

	#next step would be to make a difference graph and then perform hierarchical clustering
	#(divisive would be better than agglomerative).

file = open('keylookup.pickle')
keyLookup = pickle.load(file)
file.close()
keyLookup['nothing']='Nothing'
keyLookup['']='Nothing'




filename = 'Stats/'+str(sys.argv[1])+'.txt'
file = open(filename)
table=file.readlines()
file.close()

#'real' usage screwed me over--I can't take total count from header
#using percentages is a bad idea because of roundoff

for i in range(6,len(table)):
	name = table[i][10:29]

	if (name[0] == '-'):
		break

	while name[len(name)-1] == ' ': 
		#remove extraneous spaces
		name = name[0:len(name)-1]
	if name == 'empty':
		continue

	count = table[i][31:38]
	while count[len(count)-1] == ' ':
		#remove extraneous spaces
		count = count[0:len(count)-1]
	pct = table[i][39:46]

	if float(pct) < 0.1 or int(count)<10:
		break

	movesetCounter('Raw/moveset/'+str(sys.argv[1])+'/'+keyify(name)+'.txt')

	

	
	
	
