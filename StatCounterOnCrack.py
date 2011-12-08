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
teamCount = 0
counter = [0 for i in range(len(lsnum))]
realCounter = [0 for i in range(len(lsnum))]
turnCounter = [0 for i in range(len(lsnum))]
KOcounter = [0 for i in range(len(lsnum))]
TCsquared = [0 for i in range(len(lsnum))] #for calculating std. dev
KCsquared = [0 for i in range(len(lsnum))] #	"
encounterMatrix = [[[0 for k in range(9)] for j in range(len(lsnum))] for i in range(len(lsnum))]
trainerNextLine=True
eventNextLine=False
for entry in range(0,len(species)):
	#print entry
	found = False
	if trainerNextLine:
		trainer = species[entry]
		trainerNextLine = False
		ctemp = []
		turnt = []
		KOtemp = []
	elif eventNextLine:
		if species[entry] == "---\n":
			eventNextLine = False
			trainerNextLine = True
			battleCount=battleCount+1
		elif len(sys.argv)>2:
			poke1 = species[entry][0:string.find(species[entry]," vs.")]
			poke2 = species[entry][string.find(species[entry]," vs.")+5:string.find(species[entry],":")]
			event = species[entry][string.find(species[entry],":")+2:len(species[entry])-1]
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
				encounterMatrix[i][j][e] = encounterMatrix[i][j][e]+1
				encounterMatrix[j][i][f] = encounterMatrix[j][i][f]+1

	elif species[entry] == "***\n" or species[entry] == "@@@\n":
		if species[entry] == "***\n":
			trainerNextLine = True
		else:
			eventNextLine = True
		#decide whether to count the team or not
		#if you were going to compare the trainer name against a database,
		#you'd do it here.
		#if len(ctemp) == 6: #only count teams with all six pokemon
		for i in range(len(ctemp)):
			counter[ctemp[i]] = counter[ctemp[i]]+1.0 #rather than weighting equally, we
			turnCounter[ctemp[i]] = turnCounter[ctemp[i]]+turnt[i]
			TCsquared[ctemp[i]] = TCsquared[ctemp[i]]+turnt[i]*turnt[i]
			KOcounter[ctemp[i]] = KOcounter[ctemp[i]]+KOtemp[i]
			KCsquared[ctemp[i]] = KCsquared[ctemp[i]]+KOtemp[i]*KOtemp[i]
			if turnt[i] > 0:
				realCounter[ctemp[i]] = realCounter[ctemp[i]]+1.0
			#could use the trainer ratings db to weight these... 
		teamCount = teamCount+1
			
	else:
		stemp = species[entry][0:string.rfind(species[entry]," (")]+"\n"
		KOs = eval(species[entry][string.rfind(species[entry]," (")+2:string.rfind(species[entry],",")])
		turns = eval(species[entry][string.rfind(species[entry],",")+1:string.rfind(species[entry],")")])
		if stemp != "???\n":
			for i in range(0,len(lsnum)):
				if stemp == lsname[i]:
					ctemp.append(i)
					turnt.append(turns)
					KOtemp.append(KOs)
					found = True
					break
			if not found:
				print stemp+" not found!"
				sys.exit()
if len(sys.argv)>2:
	pickle.dump(encounterMatrix,open(sys.argv[2],"w"))

total = sum(counter)
realTotal = sum(realCounter)

pokes = []
for i in range(0,len(lsname)):
	pokes.append([lsname[i][0:len(lsname[i])-1],counter[i],realCounter[i],KOcounter[i],KCsquared[i],turnCounter[i],TCsquared[i]])
	#for j in range(0,len(lsname)):
	#	pokes[i][3] = pokes[i][3] + encounterMatrix[i][j][1]+encounterMatrix[i][j][2]
	

#for appearance-only form variations, we gotta manually correct (blegh)
for j in range(1,7):
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

#divide only AFTER you've summed the formes (you moron)
for i in range(len(lsnum)):
	if pokes[i][2] > 0:
		pokes[i][3] = 1.0*pokes[i][3]/pokes[i][2]
		if pokes[i][4]/pokes[i][2]-pokes[i][3]*pokes[i][3] <0:
			print "WTF?"
			print pokes[i]
			sys.exit()
		pokes[i][4] = math.sqrt(pokes[i][4]/pokes[i][2]-pokes[i][3]*pokes[i][3])
		pokes[i][5] = 1.0*pokes[i][5]/pokes[i][2]
		pokes[i][6] = math.sqrt(pokes[i][6]/pokes[i][2]-pokes[i][5]*pokes[i][5])

#sort by usage
pokes=sorted(pokes, key=lambda pokes:-pokes[1])
p=[]
l=1
print " Total battles: "+str(battleCount)
print " Total teams: "+str(teamCount)
print " Total pokemon: "+str(int(total))
print " + ---- + --------------- + ------ + ------- + ------ + ------- + "
print " | Rank | Pokemon         | Usage  | Percent | RealUse| RealPct | "
print " + ---- + --------------- + ------ + ------- + ------ + ------- + "
for i in range(0,len(pokes)):
	if pokes[i][1] == 0:
		break
	
	print ' | %-4d | %-15s | %-6d | %6.3f%% | %-6d | %6.3f%% | ' % (l,pokes[i][0],pokes[i][1],100.0*pokes[i][1]/total*6.0,pokes[i][2],100.0*pokes[i][2]/realTotal*6.0)
	p.append(pokes[i])
	l=l+1
print " + ---- + --------------- + ------ + ------- + ------ + ------- +"
#csv output
#for i in range(len(lsnum)):
#	if (counter[i] > 0):
#		print lsnum[i]+","+lsname[i][0:len(lsname[i])-1]+","+str(counter[i])+","+str(round(100.0*counter[i]/battleCount/2,5))+"%"


