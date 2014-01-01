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
	for mega in megas:
		if keyify(species) == mega[0]:
			try:
				megastats.append([species,stats['data'][species]['Items'][mega[1]]])
				break
			except KeyError:
				break

megastats=sorted(megastats, key=lambda megastats:-megastats[1])
for mega in megastats:
	print "%-18s%8.5f%%" % (mega[0],600.0*mega[1]/total)

