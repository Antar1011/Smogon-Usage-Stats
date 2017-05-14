#!/usr/bin/env python

"""The goal of this script is to take a json version of the "exports" object
used on Pokemon Showdown and pull out the data that's needed for the scripts."""

import json
import cPickle as pickle
from onix import contexts

ctx = contexts.get_standard_context(force_refresh=True)

keyLookup = {}
baseStats = {}
types = {}

for item in ctx.items.values():
    keyLookup[item['id']] = item['name']

for key, move in ctx.moves.items():
    keyLookup[key] = move['name']

for ability in ctx.abilities.values():
    keyLookup[ability['id']] = ability['name']

for k, v in ctx.pokedex.items():
    baseStats[k] = v['baseStats']
    keyLookup[k] = v['species']
    types[k] = v['types']

for k, v in ctx.natures.items():
    keyLookup[k] = v['name']

json.dump(baseStats, open('baseStats.json', 'w+'))
json.dump(types, open('types.json', 'w+'))
pickle.dump(keyLookup, open('keylookup.pickle', 'w+'))
