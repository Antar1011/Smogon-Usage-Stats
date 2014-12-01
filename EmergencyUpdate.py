import string
import sys
import json
import cPickle as pickle
from common import keyify,getUsage

file = open('keylookup.pickle')
keyLookup = pickle.load(file)
file.close()
file=open('formats-data.json')
raw = file.readline()
file.close()

#in case the user copy/pasted with the quotes still on
if raw[0] == '"':
	raw=raw[1:]
if raw[len(raw)-1] == '"':
	raw=raw[:len(raw)-1]

formatsData = json.loads(raw)

curTiers = {}
NFE=[]
for poke in formatsData:
	if poke in ['pichuspikyeared', 'unownb', 'unownc', 'unownd', 'unowne', 'unownf', 'unowng', 'unownh', 'unowni', 'unownj', 'unownk', 'unownl', 'unownm', 'unownn', 'unowno', 'unownp', 'unownq', 'unownr', 'unowns', 'unownt', 'unownu', 'unownv', 'unownw', 'unownx', 'unowny', 'unownz', 'unownem', 'unownqm', 'burmysandy', 'burmytrash', 'cherrimsunshine', 'shelloseast', 'gastrodoneast', 'deerlingsummer', 'deerlingautumn', 'deerlingwinter', 'sawsbucksummer', 'sawsbuckautumn', 'sawsbuckwinter', 'keldeoresolution', 'genesectdouse', 'genesectburn', 'genesectshock', 'genesectchill', 'basculinbluestriped', 'darmanitanzen','keldeoresolute']:
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
	if old in ['NFE','LC']:
		NFE.append(poke)
	if old == 'Illegal':
		continue
	elif old not in ['Uber','OU','BL','UU','BL2','RU','BL3','NU','BL4','PU']:
		old = 'PU'
	curTiers[poke]=old

usage = {} #track usage across all relevant tiers [OU,UU,RU,NU]

getUsage(str(sys.argv[1])+"/Stats/ou-1695.txt",0,24.0,usage) #OU
getUsage(str(sys.argv[1])+"/Stats/uu-1630.txt",1,24.0,usage) #UU
getUsage(str(sys.argv[1])+"/Stats/ru-1630.txt",2,24.0,usage) #RU
getUsage(str(sys.argv[1])+"/Stats/nu-1630.txt",3,24.0,usage) #NU

newTiers={}
#start with Ubers
for poke in curTiers.keys():
	if curTiers[poke] == 'Uber':
		newTiers[poke] = 'Uber'

#next do the OU rises
for poke in curTiers.keys():
	if poke not in usage:
		continue
	if usage[poke][0] > 0.06696700846 and poke not in newTiers.keys():
		newTiers[poke] = 'OU'

#next do the UU drops
for poke in curTiers.keys():
	if curTiers[poke] == 'OU' and poke not in newTiers.keys():
		if usage[poke][0] < 0.01717940145:
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
	if usage[poke][1] > 0.06696700846 and poke not in newTiers.keys():
		newTiers[poke] = 'UU'

#next do the RU drops
for poke in curTiers.keys():
	if curTiers[poke] == 'UU' and poke not in newTiers.keys():
		if usage[poke][1] < 0.01717940145:
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
	if usage[poke][2] > 0.06696700846 and poke not in newTiers.keys():
		newTiers[poke] = 'RU'

#next do the NU drops
for poke in curTiers.keys():
	if curTiers[poke] == 'RU' and poke not in newTiers.keys():
		if usage[poke][2] < 0.01717940145:
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
	if usage[poke][3] > 0.06696700846 and poke not in newTiers.keys():
		newTiers[poke] = 'NU'

#next do the PU drops
for poke in curTiers.keys():
	if curTiers[poke] == 'NU' and poke not in newTiers.keys():
		if usage[poke][3] < 0.01717940145:
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

for poke in curTiers:
	if curTiers[poke] != newTiers[poke]:
		print keyLookup[poke]+" moved from "+curTiers[poke]+" to "+newTiers[poke]


