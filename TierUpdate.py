import string
import sys
import json
import cPickle as pickle
from common import keyify,readTable,getBattleFormatsData

def getUsage(filename,col,weight,usage):
	tempUsage, nBattles = readTable(filename)
	for i in tempUsage:
		if keyify(i) not in usage:
			usage[keyify(i)]=[0,0,0,0,0]
		if i != 'empty':
			usage[keyify(i)][col] = usage[keyify(i)][col]+weight*6.0*tempUsage[i]/sum(tempUsage.values())/24

def makeTable(table,name,keyLookup):

	print "[HIDE="+name+"][CODE]"
	print "Combined usage for "+name
	print " + ---- + ------------------ + ------- + "
	print " | Rank | Pokemon            | Percent | "
	print " + ---- + ------------------ + ------- + "
	print ' | %-4d | %-18s | %6.3f%% |' % (1,keyLookup[table[0][0]],table[0][1]*100)
	for i in range(1,len(table)):
		if table[i][1] < 0.001:
			break
		print ' | %-4d | %-18s | %6.3f%% |' % (i+1,keyLookup[table[i][0]],100.0*table[i][1])
	print " + ---- + ------------------ + ------- + "
	print "[/CODE][/HIDE]"

tiers = ['Uber','OU','BL','UU','BL2','RU','BL3','NU','BL4','PU']
usageTiers = ['ou', 'uu', 'ru', 'nu', 'pu']

def main(months):
	file = open('keylookup.pickle')
	keyLookup = pickle.load(file)
	file.close()

	rise =  [0.06696700846,0.04515839608,0.03406367107][len(months)-1]
	drop =  [0.01717940145,0.02284003156,0.03406367107][len(months)-1]

	formatsData = getBattleFormatsData()

	curTiers = {}
	NFE=[]
	for poke in formatsData:
		if poke in ['pichuspikyeared', 'unownb', 'unownc', 'unownd', 'unowne', 'unownf', 'unowng', 'unownh', 'unowni', 'unownj', 'unownk', 'unownl', 'unownm', 'unownn', 'unowno', 'unownp', 'unownq', 'unownr', 'unowns', 'unownt', 'unownu', 'unownv', 'unownw', 'unownx', 'unowny', 'unownz', 'unownem', 'unownqm', 'burmysandy', 'burmytrash', 'cherrimsunshine', 'shelloseast', 'gastrodoneast', 'deerlingsummer', 'deerlingautumn', 'deerlingwinter', 'sawsbucksummer', 'sawsbuckautumn', 'sawsbuckwinter', 'keldeoresolution', 'genesectdouse', 'genesectburn', 'genesectshock', 'genesectchill', 'basculinbluestriped', 'darmanitanzen','keldeoresolute','pikachucosplay']:
			continue
		if 'isNonstandard' in formatsData[poke]:
			if formatsData[poke]['isNonstandard']:
				continue
		#if 'requiredItem' in formatsData[poke]:
		#		continue
		#if poke == 'rayquazamega':
		#	continue
		if 'tier' not in formatsData[poke].keys():
			continue
		old = formatsData[poke]['tier']
		if old[0] == '(':
			old = old[1:-1]
		if old in ['NFE','LC']:
			NFE.append(poke)
		if old == 'Illegal' or old == 'Unreleased':
			continue
		elif old not in tiers:
			old = tiers[-1]
		curTiers[poke]=old

	usage = {} #track usage across all relevant tiers [OU,UU,RU,NU]

	remaining=24.0
	for i in xrange(len(months)):
		weight = remaining
		if i + 1 < len(months):
			if i == 0:
				weight = 20.0
			if i == 1:
				weight = 3.0
		remaining -= weight

		for j in xrange(len(usageTiers)):		
			n = {}
			u = {}

			baseline = "1630"
			if usageTiers[j] in ['ou']:
				baseline = "1695"
			for k in ('', 'suspecttest', 'alpha', 'beta'):
				try:
					u[k], n[k] = readTable(months[i]+"/Stats/gen7"+usageTiers[j]+k+"-"+baseline+".txt")

				except IOError:
					pass
			ntot = sum(n.values())
			
			for k in u:
				for poke in u[k]:
					if keyify(poke) not in usage:
						usage[keyify(poke)]=[0]*len(usageTiers)
					if poke != 'empty':
						usage[keyify(poke)][j] += weight*n[k]/ntot*u[k][poke]/24

	#generate three-month tables and start working on that new tier list

	OU = []
	UU = []
	RU = []
	NU = []
	PU = []
	
	for i in usage:
		if usage[i][0] > 0.0:
			OU.append([i,usage[i][0]])
		if usage[i][1] > 0.0:
			UU.append([i,usage[i][1]])
		if usage[i][2] > 0.0:
			RU.append([i,usage[i][2]])
		if usage[i][3] > 0.0:
			NU.append([i,usage[i][3]])
		if usage[i][4] > 0.0:
			PU.append([i,usage[i][4]])

	OU = sorted(OU, key=lambda OU:-OU[1])
	UU = sorted(UU, key=lambda UU:-UU[1])
	RU = sorted(RU, key=lambda RU:-RU[1])
	NU = sorted(NU, key=lambda NU:-NU[1])
	PU = sorted(PU, key=lambda PU:-PU[1])

	makeTable(OU,"OU",keyLookup)
	makeTable(UU,"UU",keyLookup)
	makeTable(RU,"RU",keyLookup)
	makeTable(NU,"NU",keyLookup)
	makeTable(PU,"PU",keyLookup)

	newTiers={}
	#start with Ubers
	for poke in curTiers.keys():
		if curTiers[poke] == 'Uber':
			newTiers[poke] = 'Uber'

	for poke in curTiers.keys():
		if poke not in usage:
			newTiers[poke] = curTiers[poke]

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

	#next do BL
	for poke in curTiers.keys():
		if poke not in usage:
			continue
		if curTiers[poke] == 'BL' and poke not in newTiers.keys():
			newTiers[poke] = 'BL'

	
	#next do the UU rises
	for poke in curTiers.keys():
		if poke not in usage:
			continue
		if usage[poke][1] > rise and poke not in newTiers.keys():
			newTiers[poke] = 'UU'

	#next do the RU drops
	for poke in curTiers.keys():
		if poke not in usage:
			continue
		if curTiers[poke] == 'UU' and poke not in newTiers.keys():
			if usage[poke][1] < drop:
				newTiers[poke] = 'RU'
			else:
				newTiers[poke] = 'UU'

	#next do BL2
	for poke in curTiers.keys():
		if poke not in usage:
			continue
		if curTiers[poke] == 'BL2' and poke not in newTiers.keys():
			newTiers[poke] = 'BL2'
	
	#next do the RU rises
	for poke in curTiers.keys():
		if poke not in usage:
			continue
		if usage[poke][2] > rise and poke not in newTiers.keys():
			newTiers[poke] = 'RU'

	#next do the NU drops
	for poke in curTiers.keys():
		if curTiers[poke] == 'RU' and poke not in newTiers.keys():
			if usage[poke][2] < drop:
				newTiers[poke] = 'NU'
			else:
				newTiers[poke] = 'RU'

	#next do BL3
	for poke in curTiers.keys():
		if curTiers[poke] == 'BL3' and poke not in newTiers.keys():
			newTiers[poke] = 'BL3'
	
	#next do the NU rises
	for poke in curTiers.keys():
		if poke not in usage:
			continue
		if usage[poke][3] > rise and poke not in newTiers.keys():
			newTiers[poke] = 'NU'

	#next do the PU drops
	for poke in curTiers.keys():
		if curTiers[poke] == 'NU' and poke not in newTiers.keys():
			if usage[poke][3] < drop:
				newTiers[poke] = 'PU'
			else:
				newTiers[poke] = 'NU'

	#next do BL4
	for poke in curTiers.keys():
		if curTiers[poke] == 'BL4' and poke not in newTiers.keys():
			newTiers[poke] = 'BL4'
	
	#the rest go in the lowest tier
	for poke in curTiers.keys():
		if poke not in newTiers.keys():
			newTiers[poke] = tiers[-1]

	print ""
	for poke in curTiers:
		if curTiers[poke] != newTiers[poke]:
			species = keyLookup[poke]
			if species.endswith('-Mega') or species.endswith('-Mega-X') or species.endswith('-Mega-Y') or species.endswith('-Primal'):
				base = keyify(species[:species.index('-')]) #none of the megas have hyphenated names
				if tiers.index(newTiers[base]) < tiers.index(newTiers[poke]): #if the base is in a higher tier
					newTiers[poke] = newTiers[base]
					continue
			print species+" moved from "+curTiers[poke]+" to "+newTiers[poke]

if __name__ == "__main__":
    main(sys.argv[1:])

