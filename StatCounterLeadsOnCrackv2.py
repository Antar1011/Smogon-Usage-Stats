#!/usr/bin/python
# -*- coding: latin-1 -*-
#This is an extremely pared down version of the StatCounter script that only generates lead usage.
#Eventually, I'll probably want to roll this into the main StatCounter script. Note that unlike
#StatCounterOnCrackv3.py, this script outputs to stdout (the console) and not a file (unless you do
#(some redirection).

import string
import sys
import math
import cPickle as pickle


filename = str(sys.argv[1])
file = open(filename)
species = file.readlines()
battleCount = 0
counter = {}
leadNextLine=False
for entry in species:
	#print entry
	if leadNextLine:
		leadNextLine = False
		if entry != "---\n":
			poke1 = entry[0:string.find(entry," vs.")]
			poke2 = entry[string.find(entry," vs.")+5:string.find(entry,":")]
			if poke1 not in counter.keys():
				counter[poke1]=0.0
			counter[poke1]=counter[poke1]+1.0
			if poke2 not in counter.keys():
				counter[poke2]=0.0
			counter[poke2]=counter[poke2]+1.0
			battleCount = battleCount+1
	else:
		if entry == "@@@\n":
			leadNextLine = True
	
total = sum(counter.values())

#for appearance-only form variations and PO-PS name differences, we gotta manually combine
aliases={
	'NidoranF': ['Nidoran-F'],
	'NidoranM': ['Nidoran-M'],
	'Pichu': ['Spiky Pichu'],
	'Rotom-Mow': ['Rotom-C'],
	'Rotom-Heat': ['Rotom-H'],
	'Rotom-Frost': ['Rotom-F'],
	'Rotom-Wash': ['Rotom-W'],
	'Rotom-Fan': ['Rotom-S'],
	'Deoxys-Attack': ['Deoxys-A'],
	'Deoxys-Defense': ['Deoxys-D'],
	'Deoxys-Speed': ['Deoxys-S'],
	'Wormadam-Sandy': ['Wormadam-G'],
	'Wormadam-Trash': ['Wormadam-S'],
	'Shaymin-Sky': ['Shaymin-S'],
	'Giratina-Origin': ['Giratina-O'],
	'Unown': ['Unown-B','Unown-C','Unown-D','Unown-E','Unown-F','Unown-G','Unown-H','Unown-I','Unown-J','Unown-K','Unown-L','Unown-M','Unown-N','Unown-O','Unown-P','Unown-Q','Unown-R','Unown-S','Unown-T','Unown-U','Unown-V','Unown-W','Unown-X','Unown-Y','Unown-Z','Unown-!','Unown-?'],
	'Burmy': ['Burmy-G','Burmy-S'],
	'Castform': ['Castform-Snowy','Castform-Rainy','Castform-Sunny'],
	'Cherrim': ['Cherrim-Sunshine'],
	'Shellos': ['Shellos-East'],
	'Gastrodon': ['Gastrodon-East'],
	'Deerling': ['Deerling-Summer','Deerling-Autumn','Deerling-Winter'],
	'Sawsbuck': ['Sawsbuck-Summer','Sawsbuck-Autumn','Sawsbuck-Winter'],
	'Tornadus-Therian': ['Tornadus-T'],
	'Thundurus-Therian': ['Thundurus-T'],
	'Landorus-Therian': ['Landorus-T'],
	'Keldeo': ['Keldeo-R','Keldeo-Resolution','Keldeo-Resolute'],
	'Meloetta': ['Meloetta-S','Meloetta-Pirouette'],
	'Genesect': ['Genesect-Douse','Genesect-Burn','Genesect-Shock','Genesect-Chill','Genesect-D','Genesect-S','Genesect-B','Genesect-C'],
	'Darmanitan': ['Darmanitan-D','Darmanitan-Zen'],
	'Basculin': ['Basculin-Blue-Striped','Basculin-A'],
	'Kyurem-Black': ['Kyurem-B'],
	'Kyurem-White': ['Kyurem-W']
}	
for species in aliases:
	#first make sure that the species is in the array
	if species not in counter.keys():
		counter[species]=0.0
	for alias in aliases[species]:
		if alias in counter.keys():
			counter[species] = counter[species]+counter[alias]
			del counter[alias]

pokes = []
for i in counter:
	pokes.append([i]+[counter[i]])
#sort by usage
pokes=sorted(pokes, key=lambda pokes:-pokes[1])
print " Total battles: "+str(battleCount)
print " Total teams: "+str(battleCount*2)
print " Total pokemon: "+str(int(total))
print " + ---- + ------------------ + ------ + ------- + "
print " | Rank | Pokemon            | Usage  | Percent | "
print " + ---- + ------------------ + ------ + ------- + "
for i in range(0,len(pokes)):
	if pokes[i][1] == 0:
		break
	print ' | %-4d | %-18s | %-6d | %6.3f%% |' % (i+1,pokes[i][0],pokes[i][1],100.0*pokes[i][1]/total)
print " + ---- + ------------------ + ------ + ------- + "
#csv output
#for i in range(len(lsnum)):
#	if (counter[i] > 0):
#		print lsnum[i]+","+lsname[i][0:len(lsname[i])-1]+","+str(counter[i])+","+str(round(100.0*counter[i]/battleCount/2,5))+"%"


