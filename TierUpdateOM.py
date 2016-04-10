import string
import sys
import json
import cPickle as pickle
from common import keyify,readTable
from TierUpdate import makeTable

rise = 0.03406367107 #0.06696700846 #0.04515839608
drop = 0.03406367107 #0.01717940145 #0.02284003156

tiers = ['Uber','OU','BL','UU','BL2','RU','BL3','NU','BL4','PU']

file = open('keylookup.pickle')
keyLookup = pickle.load(file)
file.close()

def getUsage(filename,col,weight,usage):
	tempUsage, nBattles = readTable(filename)
	for i in tempUsage:
		if keyify(i) not in usage:
			usage[keyify(i)]=[0,0,0,0,0]
		if i != 'empty':
			usage[keyify(i)][col] = usage[keyify(i)][col]+weight*6.0*tempUsage[i]/sum(tempUsage.values())/24

def usageToTiers(usage):
	OU = []
	UU = []
	for i in usage:
		if usage[i][0] > 0.0:
			OU.append([i,usage[i][0]])
		if usage[i][1] > 0.0:
			UU.append([i,usage[i][1]])
	OU = sorted(OU, key=lambda OU:-OU[1])
	UU = sorted(UU, key=lambda UU:-UU[1])
	return (OU,UU)

def raiseAndDrop(curTiers,usage,lowest):
	for poke in usage:
		if poke not in curTiers:
			species = keyLookup[poke]
			if species.endswith('Mega') or species.endswith('Mega-X') or species.endswith('Mega-Y'):
				base = keyify(species[:species.index('-')]) #none of the megas have hyphenated names
				if base in curTiers:
					curTiers[poke]=curTiers[base]
			else:
				curTiers[poke]=lowest
	newTiers={}
	#start with Ubers
	for poke in curTiers.keys():
		if curTiers[poke] == 'Uber':
			newTiers[poke] = 'Uber'

	#next do the OU rises
	for poke in curTiers.keys():
		if poke not in usage:
			continue
		if usage[poke][0] > rise and poke not in newTiers.keys():
			newTiers[poke] = 'OU'

	#next do the UU drops
	for poke in curTiers.keys():
		if poke not in usage:
			continue
		if curTiers[poke] == 'OU' and poke not in newTiers.keys():
			if usage[poke][0] < drop:
				newTiers[poke] = 'UU'
			else:
				newTiers[poke] = 'OU'

	#next do the UU rises
	for poke in curTiers.keys():
		if poke not in usage:
			continue
		if usage[poke][1] > rise and poke not in newTiers.keys():
			newTiers[poke] = 'UU'

	#next do the NU drops
	for poke in curTiers.keys():
		if curTiers[poke] == 'UU' and poke not in newTiers.keys():
			if usage[poke][1] < drop:
				newTiers[poke] = 'NU'
			else:
				newTiers[poke] = 'UU'

	#the rest are NU
	for poke in curTiers.keys():
		if poke not in newTiers.keys():
			newTiers[poke] = 'NU'

	return newTiers

def main():
	file=open('formats.json')
	raw = file.readline()
	file.close()
	file = open('baseStats.json')
	baseStats = json.loads(file.readline())
	file.close()
	validPokemon=baseStats.keys()

	#in case the user copy/pasted with the quotes still on
	if raw[0] == '"':
		raw=raw[1:]
	if raw[len(raw)-1] == '"':
		raw=raw[:len(raw)-1]

	formats = json.loads(raw)
	banlists={}
	for format in formats:
		if format['name'] in ['LC','LC UU','Doubles OU', 'Doubles UU', 'Doubles NU']:
			banlist=[]
			for entry in format['banlist']:
				keyified=keyify(entry)
				if keyified in validPokemon:
					banlist.append(keyified)
			banlists[format['name']]=banlist

	curTiers= {}
	curTiers['LC']={}
	curTiers['Doubles']={}
	for poke in banlists['LC']:
		curTiers['LC'][poke]='Uber'
	for poke in banlists['LC UU']:
		if poke not in curTiers['LC'].keys():
			curTiers['LC'][poke]='OU'
	for poke in banlists['Doubles OU']:
		curTiers['Doubles'][poke]='Uber'
	for poke in banlists['Doubles UU']:
		if poke not in curTiers['Doubles'].keys():
			curTiers['Doubles'][poke]='OU'
	for poke in banlists['Doubles NU']:
		if poke not in curTiers['Doubles'].keys():
			curTiers['Doubles'][poke]='UU'

	usageLC = {}
	usageDoubles = {}

	month="."
	getUsage(month+"/Stats/lc-1630.txt",0,20.0,usageLC)
	getUsage(month+"/Stats/doublesou-1695.txt",0,20.0,usageDoubles)
	getUsage(month+"/Stats/doublesuu-1630.txt",1,20.0,usageDoubles)

	month="2015-12/redo"
	getUsage(month+"/Stats/lc-1630.txt",0,3.0,usageLC)
	getUsage(month+"/Stats/doublesou-1695.txt",0,3.0,usageDoubles)
	getUsage(month+"/Stats/doublesuu-1630.txt",1,3.0,usageDoubles)

	month="2015-11/redo"
	getUsage(month+"/Stats/lc-1630.txt",0,1.0,usageLC)
	getUsage(month+"/Stats/doublesou-1695.txt",0,1.0,usageDoubles)
	getUsage(month+"/Stats/doublesuu-1630.txt",1,1.0,usageDoubles)


	#generate three-month tables and start working on that new tier list
	newTiers={}

	print "[size=5][b]Little Cup[/b][/size]"
	(LCOU,LCUU) = usageToTiers(usageLC)
	makeTable(LCOU,"LC OU",keyLookup)
	#makeTable(LCUU,"LC UU",keyLookup)
	newTiers['LC']=raiseAndDrop(curTiers['LC'],usageLC,'UU')
	print ""
	for poke in curTiers['LC']:
		if curTiers['LC'][poke] != newTiers['LC'][poke]:
			if newTiers['LC'][poke] != 'NU':
				print keyLookup[poke]+" moved from LC "+curTiers['LC'][poke]+" to LC "+newTiers['LC'][poke]

	print ""
	print ""
	print "[size=5][b]Doubles[/b][/size]"

	(doublesOU,doublesUU) = usageToTiers(usageDoubles)
	makeTable(doublesOU,"Doubles OU",keyLookup)
	makeTable(doublesUU,"Doubles UU",keyLookup)
	
	
	newTiers['Doubles']=raiseAndDrop(curTiers['Doubles'],usageDoubles,'NU')
	print ""
	newUU = []
	for poke in curTiers['Doubles']:
		if curTiers['Doubles'][poke] != newTiers['Doubles'][poke]:
			species = keyLookup[poke]
			if species.endswith('-Mega') or species.endswith('-Mega-X') or species.endswith('-Mega-Y') or species.endswith('-Primal'):
				base = keyify(species[:species.index('-')]) #none of the megas have hyphenated names
				if tiers.index(newTiers['Doubles'][base]) < tiers.index(newTiers['Doubles'][poke]): #if the base is in a higher tier
					newTiers['Doubles'][poke] = newTiers['Doubles'][base]
					continue
			
			print keyLookup[poke]+" moved from Doubles "+curTiers['Doubles'][poke]+" to Doubles "+newTiers['Doubles'][poke]


if __name__ == "__main__":
    main()
