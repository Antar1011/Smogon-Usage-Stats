#!/usr/bin/python
# -*- coding: latin-1 -*-
#Loads an intermediate battle summary file created by LogReader and compiles usage and metagame stats, which
#are written to the appropriate folders. Also, if the user so wants, the script will generate a "matchup matrix"
#which looks at what happens when Pokemon X meets up with Pokemon Y. This could conceivably be used to come up
#with a statistical list of best checks and counters for each Pokemon, but I haven't yet made that script.

#encounterMatrix key: for entries encounterMatrix[poke1][poke2][i], i=...
#0: poke1 was KOed
#1: poke2 was KOed
#2: double down
#3: poke1 was switched out
#4: poke2 was switched out
#5: double switch
#6: poke1 was forced out
#7: poke2 was forced out
#8: poke1 was u-turn KOed
#9: poke2 was u-turn KOed
#10: no clue what happened

import string
import sys
import math
import cPickle as pickle
import os


filename = str(sys.argv[1])
file = open(filename)
species = file.readlines()
file.close()

tier = sys.argv[1][string.rfind(sys.argv[1],'/')+1:string.rfind(sys.argv[1],'.')]
filename="Stats/"+tier+".txt"
d = os.path.dirname(filename)
if not os.path.exists(d):
	os.makedirs(d)
usagefile=open(filename,'w')
filename="Stats/metagame/"+tier+".txt"
d = os.path.dirname(filename)
if not os.path.exists(d):
	os.makedirs(d)
metagamefile=open(filename,'w')
filename="Raw/moveset/"+tier+"/teammate.pickle"
teammatefile=open(filename,'w')
filename="Raw/moveset/"+tier+"/encounterMatrix.pickle"
encounterfile=open(filename,'w')


battleCount = 0
teamCount = 0
counter = {}
realCounter = {}
turnCounter = {}
KOcounter = {}
TCsquared = {} #for calculating std. dev
KCsquared = {} #	"
encounterMatrix = {}
teammateMatrix = {}
tagCounter = {}
stallCounter = []
metricCounter = []

trainerNextLine=True
eventNextLine=False
for entry in species:
	#print entry
	if trainerNextLine:		
		i = string.rfind(entry,' (')
		trainer = entry[:i]
		j = string.find(entry,',',i+7)
		bias = int(entry[i+7:j])
		i = string.find(entry,',',j+13)
		stalliness = float(entry[j+13:i])
		tags = entry[i+7:string.find(entry,')',i+7)].split(',')
		
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
			fodder = False
			if (event == "double down"):
				e = f = 2
			elif (event == "double switch"):
				e = f = 5
			elif (event == "no clue what happened"):
				e = f = 10
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
				if (event2 == "KOed"):
					e = p
					f = (p+1)%2
				elif (event2 == "u-turn KOed"):
					e=p+8
					f=(p+1)%2+8
				elif (event2 == "switched out"):
					e = p+3
					f = (p+1)%2+3
				elif (event2 == "forced out"):
					e = p+6
					f = (p+1)%2+6
				elif (event2 == "foddered"):
					fodder = True 
				else:
					print "Houston, we have a problem."
					print event2
					sys.exit()
			if not fodder: #we don't record fodderings
				#see if matchup is already in arrays. If not, add it
				if poke1 not in encounterMatrix.keys():
					encounterMatrix[poke1]={}
				if poke2 not in encounterMatrix.keys():
					encounterMatrix[poke2]={}
				if poke2 not in encounterMatrix[poke1].keys():
					encounterMatrix[poke1][poke2]=[0 for k in range(11)]
				if poke1 not in encounterMatrix[poke2].keys():
					encounterMatrix[poke2][poke1]=[0 for k in range(11)]
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
			if ctemp[i] not in teammateMatrix.keys():
				teammateMatrix[ctemp[i]]={}
			for j in range(len(ctemp)):
				if i is not j:
					if ctemp[j] not in teammateMatrix[ctemp[i]].keys():
						teammateMatrix[ctemp[i]][ctemp[j]]=0.0
					teammateMatrix[ctemp[i]][ctemp[j]]=teammateMatrix[ctemp[i]][ctemp[j]]+1.0
		
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
		for tag in tags:
			if tag not in tagCounter.keys():
				tagCounter[tag] = 0.0
			tagCounter[tag] = tagCounter[tag]+1.0
		stallCounter.append(stalliness)
		if entry == "***\n":
			totalKOs = float(sum(KOtemp))
			biasp = bias
		else:
			totalKOs = totalKOs+float(sum(KOtemp))
			totalTurns = float(sum(turnt))
			if (totalKOs > 0):
				metricCounter.append([biasp,bias,stallCounter[len(stallCounter)-2],stalliness,totalTurns/totalKOs])
			
		teamCount = teamCount+1
			
	else:
		stemp = entry[0:string.rfind(entry," (")]
		KOs = float(entry[string.rfind(entry," (")+2:string.rfind(entry,",")])
		turns = float(entry[string.rfind(entry,",")+1:string.rfind(entry,")")])
		if stemp != "???":
			ctemp.append(stemp)
			turnt.append(turns)
			KOtemp.append(KOs)

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
	'Kyurem-Black': ['Kyurem-B'],
	'Kyurem-White': ['Kyurem-W']
}	
if 'Empty' in pokedict.keys(): #delete no-entry slots
		del pokedict['Empty']
if 'empty' in pokedict.keys(): #delete no-entry slots
		del pokedict['empty']

for species in aliases:
	#first make sure that the species is in the array
	if species not in pokedict.keys():
		pokedict[species]=[0 for k in range(6)]
	if species not in encounterMatrix.keys():
		encounterMatrix[species]={}
	for s in encounterMatrix:
		if species not in encounterMatrix[s].keys():
			encounterMatrix[s][species]=[0 for k in range(9)]
	if species not in teammateMatrix.keys():
		teammateMatrix[species]={}
	for s in teammateMatrix:
		if species not in teammateMatrix[s].keys():
			teammateMatrix[s][species]=0.0;

	for alias in aliases[species]:
		if alias in pokedict.keys():
			for j in range(0,6):
				pokedict[species][j] = pokedict[species][j]+pokedict[alias][j]
			del pokedict[alias]
		if alias in encounterMatrix.keys():
			for s in encounterMatrix:
				for j in range(9):
					encounterMatrix[species][s][j]=encounterMatrix[species][s][j]+encounterMatrix[alias][s][j]
			del encounterMatrix[alias]
		for s in encounterMatrix:
			if alias in encounterMatrix[s].keys():
				for j in range(9):
					encounterMatrix[s][species][j]=encounterMatrix[s][species][j]+encounterMatrix[s][alias][j]
				del encounterMatrix[s][alias]
		if alias in teammateMatrix.keys():
			for s in teammateMatrix:
				teammateMatrix[species][s]=teammateMatrix[species][s]+teammateMatrix[alias][s]
			del teammateMatrix[alias]
		for s in teammateMatrix:
			if alias in teammateMatrix[s].keys():
				teammateMatrix[s][species]=teammateMatrix[s][species]+teammateMatrix[s][alias]
				del teammateMatrix[s][alias]

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


#write teammates and checkscounters to file
pickle.dump(teammateMatrix,teammatefile)
teammatefile.close()
pickle.dump(encounterMatrix,encounterfile)
encounterfile.close()

#sort by usage
pokes=sorted(pokes, key=lambda pokes:-pokes[1])
p=[]
l=1
usagefile.write(" Total battles: "+str(battleCount)+"\n")
usagefile.write(" Total teams: "+str(teamCount)+"\n")
usagefile.write(" Total pokemon: "+str(int(total))+"\n")
usagefile.write(" + ---- + ------------------ + ------ + ------- + ------ + ------- + \n")
usagefile.write(" | Rank | Pokemon            | Usage  | Percent | RealUse| RealPct | \n")
usagefile.write(" + ---- + ------------------ + ------ + ------- + ------ + ------- + \n")
for i in range(0,len(pokes)):
	if pokes[i][1] == 0:
		break
	usagefile.write(' | %-4d | %-18s | %-6d | %6.3f%% | %-6d | %6.3f%% | \n' % (l,pokes[i][0],pokes[i][1],100.0*pokes[i][1]/total*6.0,pokes[i][2],100.0*pokes[i][2]/realTotal*6.0))
	p.append(pokes[i])
	l=l+1
usagefile.write(" + ---- + ------------------ + ------ + ------- + ------ + ------- +\n\n")
usagefile.close()

#metagame analysis
tags = []
for tag in tagCounter:
	tags.append([tag,tagCounter[tag]])
tags=sorted(tags, key=lambda tags:-tags[1])

for i in range(0,len(tags)):
	line = ' '+tags[i][0]
	for j in range(len(tags[i][0]),30):
		line = line + '.'
	line = line + '%6.3f%%' % (100.0*tags[i][1]/teamCount)
	metagamefile.write(line+'\n')
metagamefile.write('\n')

#stalliness
stallCounter=sorted(stallCounter, key=lambda stallCounter:stallCounter)

#figure out a good bin range by looking at .1% and 99.9% points
low = stallCounter[len(stallCounter)/1000]
high = stallCounter[len(stallCounter)-len(stallCounter)/1000-1]

nbins = 13 #this is actually only a rough idea--I think it might be the minimum?

if (low > 0):
	low = 0.0
elif (high < 0):
	high = 0.0

binSize = (high-low)/(nbins-1)
#this is bound to be an ugly number, so let's make it pretty
for x in [10,5,2.5,2,1.5,1,0.5,0.25,0.2,0.1,0.05]:
	if binSize > x:
		break
#if binSize < 0.05, fuck it--I'm not zooming in any further
binSize = x
histogram = [[0.0,0]]
x=binSize
while x+binSize/2 < high:
	histogram.append([x,0])
	x=x+binSize
x=-binSize
while x-binSize/2 > low:
	histogram.append([x,0])
	x=x-binSize
histogram=sorted(histogram, key=lambda histogram:histogram[0])
nbins = len(histogram)

for start in range(len(stallCounter)):
	if stallCounter[start] >= histogram[0][0]-binSize/2:
		break

j=0
for i in range(start,len(stallCounter)):
	while stallCounter[i] > histogram[0][0]+binSize*(j+0.5):
		j=j+1
	if j>=len(histogram):
		break
	histogram[j][1] = histogram[j][1]+1

maximum = 0
for i in range(len(histogram)):
	if histogram[i][1] > maximum:
		maximum = histogram[i][1]

nblocks = 30 #maximum number of blocks to go across
blockSize = maximum/nblocks

if blockSize > 0:

	#print histogram
	metagamefile.write(' Stalliness (mean: %6.3f)\n'%(sum(stallCounter)/teamCount))
	for i in range(len(histogram)):
		if histogram[i][0]%(2.0*binSize) < binSize/2:
			line = ' '
			if histogram[i][0]>0.0:
				line=line+'+'
			elif histogram[i][0] == 0.0:
				line=line+' '
			line = line+'%3.1f|'%(histogram[i][0])
		else:
			line = '     |'
		for j in range(int((histogram[i][1]+blockSize/2)/blockSize)):#poor man's rounding
			line = line + '#'
		metagamefile.write(line+'\n')
	metagamefile.write(' more negative = more offensive, more positive = more stall\n')
	metagamefile.write(' one # = %d teams (%5.2f%%)\n'%(blockSize,100.0*blockSize/teamCount))

metagamefile.close()
#outfile=open('stall.dat','w')
#for line in metricCounter:
#	for item in line:
#		outfile.write(str(item)+'\t')
#	outfile.write('\n')
#outfile.close()

