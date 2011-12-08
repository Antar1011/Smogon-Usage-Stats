#!/usr/bin/python
# -*- coding: latin-1 -*-

import string
import sys
import math
import cPickle as pickle


file = open("pokemons.txt")
pokelist = file.readlines()
file.close()

lsnum = []
lsname = []
for line in range(0,len(pokelist)):
	lsnum.append(pokelist[line][0:str.find(pokelist[line],':')])
	lsname.append(pokelist[line][str.find(pokelist[line],' ')+1:len(pokelist[line])])
filename = str(sys.argv[1])
file = open(filename)
species = file.readlines()
battleCount = 0
counter = [0 for i in range(len(lsnum))]
leadNextLine=False
for entry in range(0,len(species)):
	#print entry
	found = False
	
	if leadNextLine:
		leadNextLine = False
		if species[entry] != "---\n":
			poke1 = species[entry][0:string.find(species[entry]," vs.")]
			poke2 = species[entry][string.find(species[entry]," vs.")+5:string.find(species[entry],":")]
		
			#ID pokemon involved
			for i in range(0,len(lsnum)):
				if poke1+"\n" == lsname[i]:
					break
			if i == len(lsnum):
				print poke1+" not found!"
				sys.exit()
			for j in range(0,len(lsnum)):
				if poke2+"\n" == lsname[j]:
					break
			if j == len(lsnum):
				print poke2+" not found!"
				sys.exit()

			counter[i] = counter[i]+1
			counter[j] = counter[j]+1
			battleCount = battleCount+1
	else:
		if species[entry] == "@@@\n":
			leadNextLine = True
total = sum(counter)
pokes = []
for i in range(0,len(lsname)):
	pokes.append([lsname[i][0:len(lsname[i])-1],counter[i]])
	#for j in range(0,len(lsname)):
	#	pokes[i][3] = pokes[i][3] + encounterMatrix[i][j][1]+encounterMatrix[i][j][2]
	

#for appearance-only form variations, we gotta manually correct (blegh)
j=1
pokes[172][j] = pokes[172][j] + pokes[173][j] #spiky pichu
for i in range(507,534):
	pokes[202][j] = pokes[202][j]+pokes[i][j] #unown
pokes[352][j] = pokes[352][j] + pokes[553][j] + pokes[554][j] + pokes[555][j] #castform--if this is an issue, I will be EXTREMELY surprised
pokes[413][j] = pokes[413][j] + pokes[551][j] + pokes[552][j] #burmy
pokes[422][j] = pokes[422][j] + pokes[556][j]  #cherrim
pokes[423][j] = pokes[423][j] + pokes[557][j] #shellos
pokes[424][j] = pokes[424][j] + pokes[558][j] #gastrodon
pokes[615][j] = pokes[615][j] + pokes[616][j] #basculin
pokes[621][j] = pokes[621][j] + pokes[622][j] #darmanitan
pokes[652][j] = pokes[652][j] + pokes[653][j] + pokes[654][j] + pokes[655][j] #deerling
pokes[656][j] = pokes[656][j] + pokes[657][j] + pokes[658][j] + pokes[659][j] #sawsbuck
pokes[721][j] = pokes[721][j] + pokes[722][j] #meloetta
for i in range(507,534):
	pokes[i][j] = 0
pokes[173][j] = pokes[553][j] = pokes[554][j] = pokes[555][j] = pokes[551][j] = pokes[552][j] = pokes[556][j] = pokes[557][j] = pokes[558][j] = pokes[616][j] = pokes[622][j] = pokes[653][j] = pokes[654][j] = pokes[655][j] = pokes[657][j] = pokes[658][j] = pokes[659][j] = pokes[722][j] = 0

#sort by usage
pokes=sorted(pokes, key=lambda pokes:-pokes[1])
print " Total battles: "+str(battleCount)
print " Total teams: "+str(battleCount*2)
print " Total pokemon: "+str(int(total))
print " + ---- + --------------- + ------ + ------- + "
print " | Rank | Pokemon         | Usage  | Percent | "
print " + ---- + --------------- + ------ + ------- + "
for i in range(0,len(pokes)):
	if pokes[i][1] == 0:
		break
	print ' | %-4d | %-15s | %-6d | %6.3f%% |' % (i+1,pokes[i][0],pokes[i][1],100.0*pokes[i][1]/total)
print " + ---- + --------------- + ------ + ------- + "
#csv output
#for i in range(len(lsnum)):
#	if (counter[i] > 0):
#		print lsnum[i]+","+lsname[i][0:len(lsname[i])-1]+","+str(counter[i])+","+str(round(100.0*counter[i]/battleCount/2,5))+"%"


