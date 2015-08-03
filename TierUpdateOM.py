import string
import sys
import json
import cPickle as pickle
from common import keyify,getUsage
from TierUpdate import makeTable

rise = 0.03406367107 #0.06696700846 #0.04515839608
drop = 0.03406367107 #0.01717940145 #0.02284003156

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

def raiseAndDrop(curTiers,usage):
	for poke in usage:
		if poke not in curTiers:
			curTiers[poke]='UU'
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
	file = open('keylookup.pickle')
	keyLookup = pickle.load(file)
	file.close()
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
		if format['name'] in ['LC','LC UU','Doubles OU', 'Doubles UU']:
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
		curTiers['LC'][poke]='OU'
	for poke in banlists['Doubles OU']:
		curTiers['Doubles'][poke]='Uber'
	for poke in banlists['Doubles UU']:
		curTiers['Doubles'][poke]='OU'

	usageLC = {}
	usageDoubles = {}

	month="."
	getUsage(month+"/Stats/lc-1630.txt",0,20.0,usageLC)
	getUsage(month+"/Stats/lcuu-1630.txt",1,20.0,usageLC)
	getUsage(month+"/Stats/doublesou-1695.txt",0,20.0,usageDoubles)
	getUsage(month+"/Stats/doublesuu-1630.txt",1,20.0,usageDoubles)

	month="2015-06"
	getUsage(month+"/Stats/lc-1630.txt",0,3.0,usageLC)
	getUsage(month+"/Stats/doublesou-1695.txt",0,3.0*88415/(88415+57448),usageDoubles)
	getUsage(month+"/Stats/doublesoususpecttest-1695.txt",0,3.0*57448/(88415+57448),usageDoubles)
	getUsage(month+"/Stats/doublesuu-1630.txt",1,3.0,usageDoubles)

	month="2015-05"
	getUsage(month+"/Stats/lc-1630.txt",0,1.0,usageLC)
	getUsage(month+"/Stats/lcuu-1630.txt",1,1.0,usageLC)
	getUsage(month+"/Stats/doublesou-1695.txt",0,1.0*117583/(117583+46798),usageDoubles)
	getUsage(month+"/Stats/doublesoususpecttest-1695.txt",0,1.0*117583/(117583+46798),usageDoubles)
	getUsage(month+"/Stats/doublesuu-1630.txt",1,1.0,usageDoubles)


	#generate three-month tables and start working on that new tier list
	newTiers={}

	print "[size=5][b]Little Cup[/b][/size]"
	(LCOU,LCUU) = usageToTiers(usageLC)
	makeTable(LCOU,"LC OU",keyLookup)
	#makeTable(LCUU,"LC UU",keyLookup)
	newTiers['LC']=raiseAndDrop(curTiers['LC'],usageLC)
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
	
	
	newTiers['Doubles']=raiseAndDrop(curTiers['Doubles'],usageDoubles)
	print ""
	initialUU = []
	for poke in curTiers['Doubles']:
		if newTiers['Doubles'][poke] == 'UU':
			initialUU.append(poke)
		if curTiers['Doubles'][poke] != newTiers['Doubles'][poke]:
			if newTiers['Doubles'][poke] != 'NU':
				print keyLookup[poke]+" moved from Doubles "+curTiers['Doubles'][poke]+" to Doubles "+newTiers['Doubles'][poke]

	initialUU = sorted(initialUU)
	print ""
	printme = "[b]Doubles NU banlist:[/b] "
	for poke in initialUU:
		printme += keyLookup[poke]+', '
	printme = printme[:-2]
	print printme





	
	

	

if __name__ == "__main__":
    main()
