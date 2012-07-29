#!/usr/bin/python
# -*- coding: latin-1 -*-

import string
import sys
import math
import cPickle as pickle


filename = str(sys.argv[1])
file = open(filename)
species = file.readlines()
battleCount = 0
teamCount = 0
counter = {}
realCounter = {}
turnCounter = {}
KOcounter = {}
TCsquared = {} #for calculating std. dev
KCsquared = {} #	"
encounterMatrix = {}
trainerNextLine=True
eventNextLine=False
for entry in species:
	#print entry
	if trainerNextLine:
		trainer = entry
		trainerNextLine = False
		ctemp = []
		turnt = []
		KOtemp = []
	elif eventNextLine:
		if entry == "---\n":
			eventNextLine = False
			trainerNextLine = True
			battleCount=battleCount+1
		elif len(sys.argv)>2:
			poke1 = entry[0:string.find(entry," vs.")]
			poke2 = entry[string.find(entry," vs.")+5:string.find(entry,":")]
			event = entry[string.find(entry,":")+2:len(entry)-1]
			#ID event type
			e = f = -1
			if (event == "double down"):
				e = f = 2
			elif (event == "double switch"):
				e = f = 5
			elif (event == "no clue what happened"):
				e = f = 8
			else:
				poke = event[0:string.find(event," was")]
				event2 = event[len(poke)+5:len(event)]
				p = 1
				if poke1 == poke:
					p = 0
				elif poke2 != poke:
					print "Houston, we have a problem."
					print entry
					sys.exit()
				if (event2 == "KOed") or (event2 == "u-turn KOed"):
					e = p
					f = (p+1)%2
				elif (event2 == "switched out"):
					e = p+3
					f = (p+1)%2+3
				elif (event2 == "forced out"):
					e = p+6
					f = (p+1)%2+6
				else:
					print "Houston, we have a problem."
					print entry
					sys.exit()

			#see if matchup is already in arrays. If not, add it
			if poke1 not in encounterMatrix.keys():
				encounterMatrix[poke1]={}
			if poke2 not in encounterMatrix[poke1].keys():
				encounterMatrix[poke1][poke2]=[0 for k in range(9)]
				encounterMatrix[poke1][poke2][e] = encounterMatrix[poke1][poke2][e]+1
				encounterMatrix[poke2][poke1][f] = encounterMatrix[poke2][poke1][f]+1

	elif entry == "***\n" or entry == "@@@\n":
		if entry == "***\n":
			trainerNextLine = True
		else:
			eventNextLine = True
		#decide whether to count the team or not
		#if you were going to compare the trainer name against a database,
		#you'd do it here.
		#if len(ctemp) == 6: #only count teams with all six pokemon
		for i in range(len(ctemp)):	
			if ctemp[i] not in counter.keys(): #see if poke is in the arrays yet. If not, add it
				counter[ctemp[i]]=0.0
				turnCounter[ctemp[i]]=0.0
				TCsquared[ctemp[i]]=0.0
				KOcounter[ctemp[i]]=0.0
				KCsquared[ctemp[i]]=0.0
				realCounter[ctemp[i]]=0.0
			counter[ctemp[i]] = counter[ctemp[i]]+1.0 #rather than weighting equally, we
								  #could use the trainer ratings db to weight these... 
			turnCounter[ctemp[i]] = turnCounter[ctemp[i]]+turnt[i]
			TCsquared[ctemp[i]] = TCsquared[ctemp[i]]+turnt[i]*turnt[i]
			KOcounter[ctemp[i]] = KOcounter[ctemp[i]]+KOtemp[i]
			KCsquared[ctemp[i]] = KCsquared[ctemp[i]]+KOtemp[i]*KOtemp[i]
			if turnt[i] > 0:
				realCounter[ctemp[i]] = realCounter[ctemp[i]]+1.0
			
		teamCount = teamCount+1
			
	else:
		stemp = entry[0:string.rfind(entry," (")]
		KOs = float(entry[string.rfind(entry," (")+2:string.rfind(entry,",")])
		turns = float(entry[string.rfind(entry,",")+1:string.rfind(entry,")")])
		if stemp != "???":
			ctemp.append(stemp)
			turnt.append(turns)
			KOtemp.append(KOs)

if len(sys.argv)>2:
	pickle.dump(encounterMatrix,open(sys.argv[2],"w"))

total = sum(counter.values())
realTotal = sum(realCounter.values())

pokedict = {}
for i in counter.keys():
	pokedict[i]=[counter[i],realCounter[i],KOcounter[i],KCsquared[i],turnCounter[i],TCsquared[i]]
	#for j in range(0,len(lsname)):
	#	pokes[i][3] = pokes[i][3] + encounterMatrix[i][j][1]+encounterMatrix[i][j][2]
	

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
	'Keldeo': ['Keldeo-R','Keldeo-Resolution'],
	'Meloetta': ['Meloetta-S','Meloetta-Pirouette'],
	'Genesect': ['Genesect-Douse','Genesect-Burn','Genesect-Shock','Genesect-Chill','Genesect-D','Genesect-S','Genesect-B','Genesect-C'],
	'Darmanitan': ['Darmanitan-D','Darmanitan-Zen'],
	'Basculin': ['Basculin-Blue-Striped','Basculin-A'],
	'Kyurem-B': ['Kyurem-Black'],
	'Kyurem-W': ['Kyurem-White']
}	
if 'Empty' in pokedict.keys(): #delete no-entry slots
		del pokedict['Empty']	
for species in aliases:
	#first make sure that the species is in the array
	if species not in pokedict.keys():
		pokedict[species]=[0 for k in range(6)]
	for alias in aliases[species]:
		if alias in pokedict.keys():
			for j in range(1,6):
				pokedict[species][j] = pokedict[species][j]+pokedict[alias][j]
			del pokedict[alias]

#divide only AFTER you've summed the formes (you moron)
for i in pokedict:
	if pokedict[i][1] > 0:
		pokedict[i][2] = 1.0*pokedict[i][2]/pokedict[i][1]
		pokedict[i][4] = 1.0*pokedict[i][4]/pokedict[i][1]
		if pokedict[i][3]/pokedict[i][1]-pokedict[i][2]*pokedict[i][2] <0:
			#print "WTF?"
			#print pokes[i]
			#sys.exit()
			pokedict[i][3] = pokedict[i][5] =  -1
			break
		pokedict[i][3] = math.sqrt(pokedict[i][3]/pokedict[i][1]-pokedict[i][2]*pokedict[i][2])
		pokedict[i][5] = math.sqrt(pokedict[i][5]/pokedict[i][1]-pokedict[i][4]*pokedict[i][4])
pokes = []
for i in pokedict:
	pokes.append([i]+pokedict[i])
#sort by usage
pokes=sorted(pokes, key=lambda pokes:-pokes[1])
p=[]
l=1
print " Total battles: "+str(battleCount)
print " Total teams: "+str(teamCount)
print " Total pokemon: "+str(int(total))
print " + ---- + ------------------ + ------ + ------- + ------ + ------- + "
print " | Rank | Pokemon            | Usage  | Percent | RealUse| RealPct | "
print " + ---- + ------------------ + ------ + ------- + ------ + ------- + "
for i in range(0,len(pokes)):
	if pokes[i][1] == 0:
		break
	print ' | %-4d | %-18s | %-6d | %6.3f%% | %-6d | %6.3f%% | ' % (l,pokes[i][0],pokes[i][1],100.0*pokes[i][1]/total*6.0,pokes[i][2],100.0*pokes[i][2]/realTotal*6.0)
	p.append(pokes[i])
	l=l+1
print " + ---- + ------------------ + ------ + ------- + ------ + ------- +"
#csv output
#for i in range(len(lsnum)):
#	if (counter[i] > 0):
#		print lsnum[i]+","+lsname[i][0:len(lsname[i])-1]+","+str(counter[i])+","+str(round(100.0*counter[i]/battleCount/2,5))+"%"


