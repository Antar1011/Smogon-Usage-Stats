#!/usr/bin/python

#The goal of this script is to take a json version of the "exports" object used on Pokemon Showdown
#and pull out the data that's needed for the scripts.

import json
import cPickle as pickle

exports=json.loads(open('exports.json').readline())

keyLookup={}
baseStats={}
types={}

for key in exports['BattleItems']:
	item = exports['BattleItems'][key]
	keyLookup[item['id']]=item['name']

for key in exports['BattleMovedex']:
	move = exports['BattleMovedex'][key]
	keyLookup[move['id']]=move['name']

for key in exports['BattleAbilities']:
	ability = exports['BattleAbilities'][key]
	keyLookup[ability['id']]=ability['name']

for key in exports['BattlePokedex']:
	poke = exports['BattlePokedex'][key]
	baseStats[key]=poke['baseStats']
	keyLookup[key]=poke['species']
	types[key]=poke['types']

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

for nature in nmod:
	keyLookup[nature] = nature.title()

json.dump(baseStats,open('baseStats.json','w+'))
json.dump(types,open('types.json','w+'))
pickle.dump(keyLookup,open('keylookup.pickle','w+'))