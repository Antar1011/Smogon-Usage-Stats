import string
import sys
import json
import cPickle as pickle
from common import keyify,getUsage

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

def main():
	file = open('keylookup.pickle')
	keyLookup = pickle.load(file)
	file.close()
	file=open('formats-data.json')
	raw = file.readline()
	file.close()

	rise =  0.06696700846#0.03406367107 #0.04515839608
	drop =  0.01717940145#0.03406367107 #0.02284003156
	#in case the user copy/pasted with the quotes still on
	if raw[0] == '"':
		raw=raw[1:]
	if raw[len(raw)-1] == '"':
		raw=raw[:len(raw)-1]

	formatsData = json.loads(raw)

	curTiers = {}
	NFE=[]
	for poke in formatsData:
		if poke in ['pichuspikyeared', 'unownb', 'unownc', 'unownd', 'unowne', 'unownf', 'unowng', 'unownh', 'unowni', 'unownj', 'unownk', 'unownl', 'unownm', 'unownn', 'unowno', 'unownp', 'unownq', 'unownr', 'unowns', 'unownt', 'unownu', 'unownv', 'unownw', 'unownx', 'unowny', 'unownz', 'unownem', 'unownqm', 'burmysandy', 'burmytrash', 'cherrimsunshine', 'shelloseast', 'gastrodoneast', 'deerlingsummer', 'deerlingautumn', 'deerlingwinter', 'sawsbucksummer', 'sawsbuckautumn', 'sawsbuckwinter', 'keldeoresolution', 'genesectdouse', 'genesectburn', 'genesectshock', 'genesectchill', 'basculinbluestriped', 'darmanitanzen','keldeoresolute','pikachucosplay']:
			continue
		if 'isNonstandard' in formatsData[poke]:
			if formatsData[poke]['isNonstandard']:
				continue
		if 'requiredItem' in formatsData[poke]:
				continue
		if poke == 'rayquazamega':
			continue
		if 'tier' not in formatsData[poke].keys():
			continue
		old = formatsData[poke]['tier']
		if old[0] == '(':
			old = old[1:-1]
		if old in ['NFE','LC']:
			NFE.append(poke)
		if old == 'Illegal' or old == 'Unreleased':
			continue
		elif old not in ['Uber','OU','BL','UU','BL2','RU','BL3','NU','BL4','PU']:
			old = 'PU'
		curTiers[poke]=old

	usage = {} #track usage across all relevant tiers [OU,UU,RU,NU]

	month="."
	getUsage(month+"/Stats/ou-1695.txt",0,20.0,usage)
	getUsage(month+"/Stats/uu-1630.txt",1,20.0*163139/(163139+168300),usage)
	getUsage(month+"/Stats/uususpecttest-1630.txt",1,20.0*168300/(163139+168300),usage)
	getUsage(month+"/Stats/ru-1630.txt",2,20.0,usage)
	getUsage(month+"/Stats/nu-1630.txt",3,20.0*95484/(95484+44655),usage)
	getUsage(month+"/Stats/nususpecttest-1630.txt",3,20.0*44655/(95484+44655),usage)
	getUsage(month+"/Stats/pu-1630.txt",4,20.0,usage)

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

	#next do BL
	for poke in curTiers.keys():
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
		if curTiers[poke] == 'UU' and poke not in newTiers.keys():
			if usage[poke][1] < drop:
				newTiers[poke] = 'RU'
			else:
				newTiers[poke] = 'UU'

	#next do BL2
	for poke in curTiers.keys():
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

	#the rest are PU
	for poke in curTiers.keys():
		if poke not in newTiers.keys():
			newTiers[poke] = 'PU'

	print ""
	for poke in curTiers:
		if curTiers[poke] != newTiers[poke]:
			print keyLookup[poke]+" moved from "+curTiers[poke]+" to "+newTiers[poke]

	print ""
	print ""
	print "[size=5][b]FU[/b][/size]"
	print "FU is an unofficial banlist based on an unofficial metagame. It is not currently supported on any simulator, but since we have usage stats for PU, and since [url=http://www.smogon.com/forums/forums/pu.327/?prefix_id=282]people have expressed interest in such a metagame[/url], here is a proper banlist:" 
	makeTable(PU,"PU",keyLookup)
	fuBanlist = []
	for poke in usage.keys():
		if newTiers[poke] == 'PU' and (usage[poke][4] >= drop or curTiers[poke] == 'NU'):
			fuBanlist.append(poke)

	fuBanlist = sorted(fuBanlist)
	printme = "[b]Banlist:[/b] "
	for poke in fuBanlist:
		printme += keyLookup[poke]+', '
	printme = printme[:-2]
	print printme

if __name__ == "__main__":
    main()

