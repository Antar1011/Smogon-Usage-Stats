import string
import sys
import json
import cPickle as pickle
from common import keyify,readTable,getFormats
from TierUpdate import makeTable

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

def raiseAndDrop(curTiers,usage,lowest,rise,drop):
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

def main(months):
	file = open('baseStats.json')
	baseStats = json.loads(file.readline())
	file.close()
	validPokemon=baseStats.keys()

	formats = json.load(open('formats.json'))

	banlists={}
	for format in ('gen7doublesou', 'gen7doublesuu'):
		banlist=[]
		for entry in formats[format]['banlist']:
			keyified=keyify(entry)
			if keyified in validPokemon:
				banlist.append(keyified)
		banlists[formats[format]['name']]=banlist

	curTiers= {}
	# curTiers['LC']={}
	curTiers['Doubles']={}
	# for poke in banlists['LC']:
	# 	curTiers['LC'][poke]='Uber'
	# for poke in banlists['LC UU']:
	# 	if poke not in curTiers['LC'].keys():
	# 		curTiers['LC'][poke]='OU'
	for poke in banlists['[Gen 7] Doubles OU']:
		curTiers['Doubles'][poke]='Uber'
	for poke in banlists['[Gen 7] Doubles UU']:
		if poke not in curTiers['Doubles'].keys():
			curTiers['Doubles'][poke]='OU'

	rise =  [0.06696700846,0.04515839608,0.03406367107][len(months)-1]
	drop =  [0.01717940145,0.02284003156,0.03406367107][len(months)-1]

	usageLC = {}
	usageDoubles = {}

	remaining=24.0
	for i in xrange(len(months)):
		weight = remaining
		if i + 1 < len(months):
			if i == 0:
				weight = 20.0
			if i == 1:
				weight = 3.0
		remaining -= weight

		nRegular = nSuspect = 0

		# try:
		# 	usageRegular, nRegular = readTable(months[i]+"/Stats/lc-1630.txt")
		# except IOError:
		# 	pass
		# try:
		# 	usageSuspect, nSuspect = readTable(months[i]+"/Stats/lcsuspecttest-1630.txt")
		# except IOError:
		# 	pass

		# if nRegular > 0:
		# 	for poke in usageRegular:
		# 		if keyify(poke) not in usageLC:
		# 			usageLC[keyify(poke)]=[0,0]
		# 		if poke != 'empty':
		# 			usageLC[keyify(poke)][0] += weight*nRegular/(nRegular+nSuspect)*usageRegular[poke]/24

		# 	if nSuspect > 0:
		# 		for poke in usageSuspect:
		# 			if keyify(poke) not in usageLC:
		# 				usageLC[keyify(poke)]=[0,0]
		# 			if poke != 'empty':
		# 				usageLC[keyify(poke)][0] += weight*nSuspect/(nRegular+nSuspect)*usageSuspect[poke]/24

		usageTiers = ['doublesou','doublesuu']
		for j in xrange(len(usageTiers)):
			nRegular = nSuspect = 0
			baseline = "1630"
			if usageTiers[j] in ['doublesou']:
				baseline = "1695"
			try:
				usageRegular, nRegular = readTable(months[i]+"/Stats/gen7"+usageTiers[j]+"-"+baseline+".txt")
			except IOError:
				pass
			try:
				usageSuspect, nSuspect = readTable(months[i]+"/Stats/gen7"+usageTiers[j]+"suspecttest-"+baseline+".txt")
			except IOError:
				pass

			if nRegular > 0:
				for poke in usageRegular:
					if keyify(poke) not in usageDoubles:
						usageDoubles[keyify(poke)]=[0]*len(usageTiers)
					if poke != 'empty':
						usageDoubles[keyify(poke)][j] += weight*nRegular/(nRegular+nSuspect)*usageRegular[poke]/24

			if nSuspect > 0:
				for poke in usageSuspect:
					if keyify(poke) not in usageDoubles:
						usageDoubles[keyify(poke)]=[0]*len(usageTiers)
					if poke != 'empty':
						usageDoubles[keyify(poke)][j] += weight*nSuspect/(nRegular+nSuspect)*usageSuspect[poke]/24

	#generate three-month tables and start working on that new tier list
	newTiers={}

	# print "[size=5][b]Little Cup[/b][/size]"
	# (LCOU,LCUU) = usageToTiers(usageLC)
	# makeTable(LCOU,"LC OU",keyLookup)
	# #makeTable(LCUU,"LC UU",keyLookup)
	# newTiers['LC']=raiseAndDrop(curTiers['LC'],usageLC,'UU',rise,drop)
	# print ""
	# for poke in curTiers['LC']:
	# 	if curTiers['LC'][poke] != newTiers['LC'][poke]:
	# 		if newTiers['LC'][poke] != 'NU':
	# 			print keyLookup[poke]+" moved from LC "+curTiers['LC'][poke]+" to LC "+newTiers['LC'][poke]

	# print ""
	# print ""
	print "[size=5][b]Doubles[/b][/size]"

	(doublesOU,doublesUU) = usageToTiers(usageDoubles)
	makeTable(doublesOU,"Doubles OU",keyLookup)
		
	newTiers['Doubles']=raiseAndDrop(curTiers['Doubles'],usageDoubles,'UU',rise,drop)
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
			if newTiers['Doubles'][poke] != 'NU':
				print keyLookup[poke]+" moved from Doubles "+curTiers['Doubles'][poke]+" to Doubles "+newTiers['Doubles'][poke]

	print ""
	print ""
	print "[size=5][b]Doubles NU[/b][/size]"
	print "Doubles NU is an unofficial metagame that's apparently so unpopular there's not even enough interest to support a challenge-only format. Still, it's conceivable that someone will want to play it, and that person should have an unofficial banlist to refer to. So..." 
	makeTable(doublesUU,"Doubles UU",keyLookup)
	dnuBanlist = []
	for poke in usageDoubles.keys():
		if poke in curTiers['Doubles']:
			if newTiers['Doubles'][poke] == 'UU' and (usageDoubles[poke][1] >= drop or curTiers['Doubles'][poke] == 'OU'):
				dnuBanlist.append(poke)

	dnuBanlist = sorted(dnuBanlist)
	printme = "[b]Banlist:[/b] "
	for poke in dnuBanlist:
		printme += keyLookup[poke]+', '
	printme = printme[:-2]
	print printme


if __name__ == "__main__":
    main(sys.argv[1:])
