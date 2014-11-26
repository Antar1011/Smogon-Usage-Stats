#!/usr/bin/python

import sys
import json
from TA import megas
from common import keyify

stats=json.load(open(sys.argv[1]))

megastats=[]
total=0
for species in stats['data'].keys():
	total += sum(stats['data'][species]['Abilities'].values())
	if keyify(species) == 'rayquaza':
		name = species
		try:
			megastats.append([name,stats['data'][species]['Moves']['dragonascent']])
		except KeyError:
			pass
	else:
		for mega in megas:
			if keyify(species) == mega[0]:
				try:
					name = species
					if mega[1][-1] in ['x','y']:
						name+=' '+mega[1][-1].upper()
					megastats.append([name,stats['data'][species]['Items'][mega[1]]])
					if mega[1][-1] != 'x':
						break
				except KeyError:
					if mega[1][-1] != 'x':
						break

megastats=sorted(megastats, key=lambda megastats:-megastats[1])
for mega in megastats:
	print "%-18s%8.5f%%" % (mega[0],600.0*mega[1]/total)

