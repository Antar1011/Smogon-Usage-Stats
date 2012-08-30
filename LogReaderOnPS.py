#!/usr/bin/python

import string
import sys
import json
import copy
import cPickle as pickle
import math
import os

def statFormula(base,lv,nat,iv,ev):
	if nat == -1: #for HP
		return (iv+2*base+ev/4+100)*lv/100+10
	else:
		return ((iv+2*base+ev/4)*lv/100+5)*nat/10

nmod = {'hardy': [10,10,10,10,10],
	'lonely': [11,9,10,10,10],
	'brave': [11,10,9,10,10],
	'adamant': [11,10,10,9,10],
	'naughty': [11,10,10,10,9],
	'bold': [9,11,10,10,10],
	'docile': [10,10,10,10,10],
	'relaxed': [10,11,9,10,10],
	'impish': [10,11,10,9,10],
	'lax': [10,11,10,10,9],
	'timid': [9,10,11,10,10],
	'hasty': [10,9,11,10,10],
	'serious': [10,10,10,10,10],
	'jolly': [10,10,11,9,10],
	'naive': [10,10,11,10,9],
	'modest': [9,10,10,11,10],
	'mild': [10,9,10,11,10],
	'quiet': [10,10,9,11,10],
	'bashful': [10,10,10,10,10],
	'rash': [10,10,10,11,9],
	'calm': [9,10,10,10,11],
	'gentle': [10,9,10,10,11],
	'sassy': [10,10,9,10,11],
	'careful': [10,10,10,9,11],
	'quirky': [10,10,10,10,10]}

def keyify(s):
	sout = ''
	for c in s:
		if c in string.uppercase:
			sout = sout + c.lower()
		elif c in string.lowercase + '1234567890':
			sout = sout + c
	return sout

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

#fix species
replacements = {
	'Rotom-H' : 'Rotom-Heat',
	'Rotom-W' : 'Rotom-Wash',
	'Rotom-F' : 'Rotom-Frost',
	'Rotom-S' : 'Rotom-Fan',
	'Rotom-C' : 'Rotom-Mow',
	'Rotom- H' : 'Rotom-Heat',
	'Rotom- W' : 'Rotom-Wash',
	'Rotom- F' : 'Rotom-Frost',
	'Rotom- S' : 'Rotom-Fan',
	'Rotom- C' : 'Rotom-Mow',
	'Rotom-h' : 'Rotom-Heat',
	'Rotom-w' : 'Rotom-Wash',
	'Rotom-f' : 'Rotom-Frost',
	'Rotom-s' : 'Rotom-Fan',
	'Rotom-c' : 'Rotom-Mow',
	'Tornadus-T' : 'Tornadus-Therian',
	'Thundurus-T' : 'Thundurus-Therian',
	'Landorus-T' : 'Landorus-Therian',
	'Deoxys-D' : 'Deoxys-Defense',
	'Deoxys-A' : 'Deoxys-Attack',
	'Deoxys-S' : 'Deoxys-Speed',
	'Kyurem-B' : 'Kyurem-Black',
	'Kyurem-W' : 'Kyurem-White',
	'Shaymin-S' : 'Shaymin-Sky',
	'Ho-oh' : 'Ho-Oh',
	"Birijion": "Virizion",
	"Terakion": "Terrakion",
	"Agirudaa": "Accelgor",
	"Randorosu": "Landorus",
	"Urugamosu": "Volcarona",
	"Erufuun": "Whimsicott",
	"Doryuuzu": "Excadrill",
	"Burungeru": "Jellicent",
	"Nattorei": "Ferrothorn",
	"Shandera": "Chandelure",
	"Roobushin": "Conkeldurr",
	"Ononokusu": "Haxorus",
	"Sazandora": "Hydreigon",
	"Chirachiino": "Cinccino",
	"Kyuremu": "Kyurem",
	"Jarooda": "Serperior",
	"Zoroaaku": "Zoroark",
	"Shinboraa": "Sigilyph",
	"Barujiina": "Mandibuzz",
	"Rankurusu": "Reuniclus",
	"Borutorosu": "Thundurus",
	"Mime Jr" : "Mime Jr.", #th== one's my fault
	#to be fair, I never observed the following, but better safe than sorry
	'Giratina-O' : 'Giratina-Origin',
	'Keldeo-R' : 'Keldeo-Resolution',
	'Wormadam-G' : 'Wormadam-Sandy',
	'Wormadam-S' : 'Wormadam-Trash',
	"Dnite": "Dragonite",
	"Ferry": "Ferrothorn",
	"Forry": "Forretress",
	"Luke":  "Lucario",
	"P2": "Porygon2",
	"Pory2": "Porygon2",
	"Pz": "Porygon-Z",
	"Poryz": "Porygon-Z",
	"Rank": "Reuniclus",
	"Ttar": "Tyranitar"
}

filename = str(sys.argv[1])
file = open(filename)
raw = file.readline()
file.close()
file = open('baseStats.pickle')
baseStats = pickle.load(file)
file.close()

tier = sys.argv[2]
rated = "Rated"

log = json.loads(raw)

#determine log type
spacelog = True
if 'log' in log.keys():
	if log['log'][0][0:2] != '| ':
		spacelog = False

#check for log length
longEnough = False
if 'log' not in log.keys():
	if int(log['turns']) > 5: 
		longEnough = True
else:
	for line in log['log']:
		if (spacelog and line[2:10] == 'turn | 6') or (not spacelog and line[1:7] == 'turn|6'):
			longEnough = True
			break
if not longEnough:
	print 'poo'
	sys.exit(0)

#get info on the trainers & pokes involved
ts = []
teams = {}

#get pokemon info
for team in ['p1team','p2team']:

	if team == 'p1team':
		trainer = log['p1']
	else:
		trainer = log['p2']

	teams[team]=[]

	for i in range(len(log[team])):
		if 'species' in log[team][i].keys():
			species = log[team][i]['species']
		else: #apparently randbats usually don't contain the species field?
			species = log[team][i]['name']

		#very odd that these == needed--I've seen ".Species", "(Species)", "species", "Species)", "SPECIES"...
		if species[0] not in string.lowercase + string.uppercase:
			species=species[1:]
		while species[len(species)-1] in ')". ':
			species=species[:len(species)-1]
		if species[0] in string.lowercase or species[1] in string.uppercase:
			species = species.title()
		if species in replacements.keys():
			species = replacements[species]

		for s in aliases: #combine appearance-only variations and weird PS quirks
			if species in aliases[s]:
				species = s
				break
		
		ts.append([trainer,species])

		if 'item' in log[team][i].keys():
			item = keyify(log[team][i]['item'])
			if item == '':
				item = 'nothing'
		else:
			item = 'nothing'
		if 'nature' in log[team][i].keys():
			nature = keyify(log[team][i]['nature'])
			if nature == '':
				nature = 'hardy'
		else:
			nature = 'hardy'
		if 'evs' in log[team][i].keys():
			evs = [int(log[team][i]['evs']['hp']),int(log[team][i]['evs']['atk']),int(log[team][i]['evs']['def']),int(log[team][i]['evs']['spa']),int(log[team][i]['evs']['spd']),int(log[team][i]['evs']['spe'])]
		else:
			evs = [0,0,0,0,0,0]
		if 'ivs' in log[team][i].keys():
			ivs = [int(log[team][i]['ivs']['hp']),int(log[team][i]['ivs']['atk']),int(log[team][i]['ivs']['def']),int(log[team][i]['ivs']['spa']),int(log[team][i]['ivs']['spd']),int(log[team][i]['ivs']['spe'])]
		else:
			ivs = [0,0,0,0,0,0]
		if 'moves' in log[team][i].keys():
			moves = log[team][i]['moves']
		else:
			moves = []
		while len(moves)<4:
			moves.append('')
		for j in range(len(moves)): #make all moves lower-case and space-free
			moves[j] = keyify(moves[j])
		#figure out Hidden Power from IVs
		if 'ability' in log[team][i].keys():
			ability = keyify(log[team][i]['ability'])
		else:
			ability = 'unknown'
		if 'level' in log[team][i].keys():
			level = int(log[team][i]['level'])
		else:
			level = 100
		stats = []
		if keyify(species) == 'shedinja':
			stats.append(1)
		else:
			stats.append(statFormula(baseStats[keyify(species)]['hp'],level,-1,ivs[0],evs[0]))
		stats.append(statFormula(baseStats[keyify(species)]['atk'],level,nmod[keyify(nature)][0],ivs[1],evs[1]))
		stats.append(statFormula(baseStats[keyify(species)]['def'],level,nmod[keyify(nature)][1],ivs[2],evs[2]))
		stats.append(statFormula(baseStats[keyify(species)]['spa'],level,nmod[keyify(nature)][3],ivs[3],evs[3]))
		stats.append(statFormula(baseStats[keyify(species)]['spd'],level,nmod[keyify(nature)][4],ivs[4],evs[4]))
		stats.append(statFormula(baseStats[keyify(species)]['spe'],level,nmod[keyify(nature)][2],ivs[5],evs[5]))

		#calculate base stalliness
		bias = evs[1]+evs[3]-evs[0]-evs[2]-evs[4]
		if keyify(species) == 'shedinja':
			stalliness = 0
		elif keyify(species) == 'ditto':
			stalliness = log(3,2) #eventually I'll want to replace this with mean stalliness for the tier
		else:
			stalliness=-math.log(((2.0*level+10)/250*max(stats[1],stats[3])/max(stats[2],stats[4])*120+2)*0.925/stats[0],2)

		#moveset modifications
		if ability in ['purepower','hugepower']:
			stalliness = stalliness - 1
		if item in ['choiceband','choicescarf','choicespecs','lifeorb']:
			stalliness = stalliness - 0.5
		if item == 'eviolite':
			stalliness = stalliness + 0.5
		if 'spikes' in moves:
			stalliness = stalliness + 0.5
		if 'toxicspikes' in moves:
			stalliness = stalliness + 0.5
		if 'toxic' in moves:
			stalliness = stalliness + 1
		if 'willowisp' in moves:
			stalliness = stalliness + 1
		if len(set(['recover' ,'slackoff', 'healorder', 'milkdrink', 'roost', 'moonlight', 'morningsun', 'synthesis', 'wish', 'aquaring', 'rest', 'softboiled', 'swallow', 'leechseed']).intersection(moves)) != 0:
			stalliness = stalliness + 1
		if ability == 'regenerator':
			stalliness = stalliness + 0.5
		if len(set(['healbell','aromatherapy']).intersection(moves)) != 0:
			stalliness = stalliness + 0.5
		if ability in ['chlorophyll', 'flareboost', 'guts', 'hustle', 'moxie', 'reckless', 'sandrush', 'solarpower', 'speedboost', 'swiftswim', 'technician', 'tintedlens', 'toxicboost', 'moody']:
			stalliness = stalliness - 0.5
		if ability in ['arenatrap','magnetpull','shadowtag']:
			stalliness = stalliness - 1
		if ability in ['dryskin', 'filter', 'hydration', 'icebody', 'intimidate', 'ironbarbs', 'marvelscale', 'naturalcure', 'magicguard', 'multiscale', 'poisonheal', 'raindish', 'roughskin', 'solidrock', 'thickfat', 'unaware']:
			stalliness = stalliness + 0.5
		if ability in ['slowstart','truant']:
			stalliness = stalliness + 1
		if item == 'lightclay':
			stalliness = stalliness - 1
		if len(set(['acupressure', 'bellydrum', 'bulkup', 'coil', 'curse', 'dragondance', 'growth', 'honeclaws', 'howl', 'meditate', 'sharpen', 'shellsmash', 'shiftgear', 'swordsdance', 'workup', 'calmmind', 'chargebeam', 'fierydance', 'nastyplot', 'tailglow', 'quiverdance', 'agility', 'autotomize', 'flamecharge', 'rockpolish', 'doubleteam', 'minimize']).intersection(moves)) != 0:
			stalliness = stalliness - 1
		if 'substitute' in moves:
			stalliness = stalliness - 0.5
		if 'protect' in moves or 'detect' in moves:
			stalliness = stalliness + 1
		if 'endeavor' in moves:
			stalliness = stalliness - 1
		if 'superfang' in moves:
			stalliness = stalliness - 0.5
		if 'trick' in moves:
			stalliness = stalliness - 0.5
		if 'psychoshift' in moves:
			stalliness = stalliness + 0.5
		if len(set(['haze', 'clearsmog', 'whirlwind', 'roar', 'circlethrow', 'dragontail', 'thunderwave', 'stunspore', 'supersonic', 'confuseray', 'swagger', 'flatter', 'teeterdance']).intersection(moves)) != 0:
			stalliness = stalliness + 0.5
		if len(set(['darkvoid', 'grasswhistle', 'hypnosis', 'lovelykiss', 'sing', 'sleeppowder', 'spore', 'yawn']).intersection(moves)) != 0:
			stalliness = stalliness + 0.5
		if item == 'redcard':
			stalliness = stalliness + 0.5
		if item == 'rockyhelmet':
			stalliness = stalliness + 0.5
		if item in ['firegem', 'watergem', 'electricgem', 'grassgem', 'icegem', 'fightinggem', 'posiongem', 'groundgem', 'groundgem', 'flyinggem', 'psychicgem', 'buggem', 'rockgem', 'ghostgem', 'darkgem', 'steelgem', 'normalgem', 'focussash', 'mentalherb', 'powerherb', 'whiteherb', 'absorbbulb', 'berserkgene', 'cellbattery', 'redcard', 'focussash', 'airballoon', 'ejectbutton', 'shedshell', 'aguavberry', 'apicotberry', 'aspearberry', 'babiriberry', 'chartiberry', 'cheriberry', 'chestoberry', 'chilanberry', 'chopleberry', 'cobaberry', 'custapberry', 'enigmaberry', 'figyberry', 'ganlonberry', 'habanberry', 'iapapaberry', 'jabocaberry', 'kasibberry', 'kebiaberry', 'lansatberry', 'leppaberry', 'liechiberry', 'lumberry', 'magoberry', 'micleberry', 'occaberry', 'oranberry', 'passhoberry', 'payapaberry', 'pechaberry', 'persimberry', 'petayaberry', 'rawstberry', 'rindoberry', 'rowapberry', 'salacberry', 'shucaberry', 'sitrusberry', 'starfberry', 'tangaberry', 'wacanberry', 'wikiberry', 'yacheberry']:
			stalliness = stalliness - 0.5
		if ability == 'harvest' or 'recycle' in moves:
			stalliness = stallines + 1
		if len(set(['jumpkick', 'doubleedge', 'submission', 'petaldance', 'hijumpkick', 'outrage', 'superpower', 'overheat', 'volttackle', 'psychoboost', 'hammerarm', 'closecombat', 'flareblitz', 'bravebird', 'dracometeor', 'leafstorm', 'woodhammer', 'headsmash', 'headcharge', 'vcreate', 'wildcharge', 'takedown']).intersection(moves)) != 0:
			stalliness = stalliness - 0.5
		if len(set(['selfdestruct', 'explosion', 'destinybond', 'perishsong', 'memento', 'healingwish', 'lunardance', 'finalgambit']).intersection(moves)) != 0:
			stalliness = stalliness - 1
		if len(set(['guillotine', 'fissure', 'sheercold']).intersection(moves)) != 0:
			stalliness = stalliness - 1

		#final correction
		stalliness=stalliness-math.log(3,2)

		teams[team].append({
			'species': keyify(species),
			'nature': nature,
			'item': item,
			'evs': evs,
			'moves': moves,
			'ability': ability,
			'bias': bias,
			'stalliness': stalliness})

		#write to moveset file
		outname = "Raw/moveset/"+tier+"/"+keyify(species)+".txt"
		d = os.path.dirname(outname)
		if not os.path.exists(d):
			os.makedirs(d)
		outfile=open(outname,'a')
		outfile.write(str(bias)+'\t'+str(stalliness)+'\t')
		outfile.write(str(level)+'\t'+ability+'\t'+item+'\t'+nature+'\t')
		for iv in ivs:
			outfile.write(str(iv)+'\t')
		for ev in evs:
			outfile.write(str(ev)+'\t')
		for move in moves:
			outfile.write(str(move)+'\t')
		outfile.write('\n')
		outfile.close()

	if len(log[team]) < 6:
		for i in range(6-len(log[team])):
			ts.append([trainer,'empty'])

	#team-type detection
	bias = stalliness = 0
	for poke in teams[team]:
		bias = bias + poke['bias']
		stalliness = stalliness + poke['stalliness']
	stalliness = stalliness / 6.0
	tags = []	

	#don't put anything before weather

	#rain
	count = 0
	detected = False
	for poke in teams[team]:
		if poke['ability'] == 'drizzle':
			detected = True
			break
		elif poke['item'] == 'damprock' and 'raindance' in poke['moves']:
			detected = True
			break
		elif 'raindance' in poke['moves']:
			count = count + 1
			if count > 1:
				detected = True
				break
	if detected:
		tags.append('rain')
	
	#sun
	count = 0
	detected = False
	for poke in teams[team]:
		if poke['ability'] == 'drought':
			detected = True
			break
		elif poke['item'] == 'heatrock' and 'sunnyday' in poke['moves']:
			detected = True
			break
		elif 'sunnyday' in poke['moves']:
			count = count + 1
			if count > 1:
				detected = True
				break
	if detected:
		tags.append('sun')

	#sand
	count = 0
	detected = False
	for poke in teams[team]:
		if poke['ability'] == 'sandstream':
			detected = True
			break
		elif poke['item'] == 'smoothrock' and 'sandstorm' in poke['moves']:
			detected = True
			break
		elif 'sandstorm' in poke['moves']:
			count = count + 1
			if count > 1:
				detected = True
				break
	if detected:
		tags.append('sand')

	#hail
	count = 0
	detected = False
	for poke in teams[team]:
		if poke['ability'] == 'snowwarning':
			detected = True
			break
		elif poke['item'] == 'icyrock' and 'hail' in poke['moves']:
			detected = True
			break
		elif 'hail' in poke['moves']:
			count = count + 1
			if count > 1:
				detected = True
				break
	if detected:
		tags.append('hail')
	if len(tags) == 4:
		tags.append('allweather')
	elif len(tags) > 1:
		tags.append('multiweather')
	elif len(tags) == 0:
		tags.append('weatherless')

	#baton pass
	count = 0
	for poke in teams[team]:
		if 'batonpass' in poke['moves']:
			if len(set(['acupressure', 'bellydrum', 'bulkup', 'coil', 'curse', 'dragondance', 'growth', 'honeclaws', 'howl', 'meditate', 'sharpen', 'shellsmash', 'shiftgear', 'swordsdance', 'workup', 'calmmind', 'chargebeam', 'fierydance', 'nastyplot', 'tailglow', 'quiverdance', 'agility', 'autotomize', 'flamecharge', 'rockpolish', 'doubleteam', 'minimize', 'substitute', 'acidarmor', 'barrier', 'cosmicpower', 'cottonguard', 'defendorder', 'defensecurl', 'harden', 'irondefense', 'stockpile', 'withdraw', 'amnesia', 'charge', 'ingrain']).intersection(poke['moves'])) != 0 or poke['ability'] in ['angerpoint', 'contrary', 'moody', 'moxie', 'speedboost']: #check for setup move/ability
				count = count + 1
				if count > 1:
					break
	if count > 1:
		tags.append('batonpass')

	#trick room
	count = [0,0]

	for poke in teams[team]:
		if 'trickroom' in poke['moves'] and 'imprison' not in poke['moves']:
			count[0] = count[0] + 1
		elif (poke['nature'] in ['brave', 'relaxed', 'quiet', 'sassy'] or baseStats[keyify(poke['species'])]['spe'] <= 50) and poke['evs'][5] < 5: #or I could just use actual stats and speed factor
			count[1] = count[1] + 1

	if (count[0] > 1 and count[1] > 1) or (count[0] > 2):
		tags.append('trickroom')
		if 'sun' in tags:
			tags.append('tricksun')
		if 'rain' in tags:
			tags.append('trickrain')
		if 'sand' in tags:
			tags.append('tricksand')
		if 'hail' in tags:
			tags.append('trickhail')	

	#gravity
	count = [0,0]

	for poke in teams[team]:
		if 'gravity' in poke['moves']:
			count[0] = count[0] + 1
		if len(set(['guillotine', 'fissure', 'sheercold', 'dynamicpunch', 'inferno', 'zapcannon', 'grasswhistle', 'sing', 'supersonic', 'hypnosis', 'blizzard', 'focusblast', 'gunkshot', 'hurricane', 'smog', 'thunder', 'clamp', 'dragonrush', 'eggbomb', 'irontail', 'lovelykiss', 'magmastorm', 'megakick', 'poisonpowder', 'slam', 'sleeppowder', 'stunspore', 'sweetkiss', 'willowisp', 'crosschop', 'darkvoid', 'furyswipes', 'headsmash', 'hydropump', 'kinesis', 'psywave', 'rocktomb', 'stoneedge', 'submission', 'boneclub', 'bonerush', 'bonemerang', 'bulldoze', 'dig', 'drillrun', 'earthpower', 'earthquake', 'magnitude', 'mudbomb', 'mudshot', 'mudslap', 'sandattack', 'spikes', 'toxicspikes']).intersection(poke['moves'])) != 0:
			count[1] = count[1] + 1

	if (count[0] > 1 and count[1] > 1) or (count[0] > 2):
		 tags.append('gravity')

	

	#voltturn
	count = 0

	for poke in teams[team]:
		if len(set(['voltswitch','uturn','batonpass']).intersection(poke['moves'])) != 0 or poke['item'] == 'ejectbutton':
			count = count + 1
			if count > 2:
				break
	if count > 2 and 'batonpass' not in tags:
		tags.append('voltturn')
	
	#dragmag and trapper
	count = [0,0]
	
	for poke in teams[team]:
		if poke['ability'] in ['magnetpull', 'arenatrap', 'shadowtag'] or len(set(['block','meanlook','spiderweb']).intersection(poke['moves'])) != 0:
			count[0] = count[0] + 1
		elif poke['species'] in ['dratini', 'dragonair', 'bagon', 'shelgon', 'axew', 'fraxure', 'haxorus', 'druddigon', 'dragonite', 'altaria', 'salamence', 'latias', 'latios', 'rayquaza', 'gible', 'gabite', 'garchomp', 'reshiram', 'zekrom', 'kyurem', 'kyuremwhite', 'kyuremblack', 'kingdra', 'vibrava', 'flygon', 'dialga', 'palkia', 'giratina', 'giratinaorigin', 'deino', 'zweilous', 'hydreigon']:
			count[1] = count[1] + 1
	if count[0] > 0 and count[1] > 1:
		tags.append('dragmag')
	if count[0] > 2:
		tags.append('trapper')

	#F.E.A.R.
	count = [0,0]
	
	for poke in teams[team]:
		if poke['ability'] == 'magicbounce' or 'rapidspin' in poke['moves']:
			count[0] = count[0]+1
		elif (poke['ability'] == 'sturdy' or poke['item'] == 'focussash') and 'endeavor' in poke['moves']:
			count[1] = count[1]+1
	if count[0] > 1 and count[1] > 2:
		tags.append('fear')
		if 'sand' in tags:
			tags.append('sandfear')
		if 'hail' in tags:
			tags.append('hailfear')
		if 'trickroom' in tags:
			tags.append('trickfear')

	#choice
	count = 0

	for poke in teams[team]:
		if poke['item'] in ['choiceband', 'choicescarf', 'choicespecs'] and poke['ability'] != 'klutz':
			count = count + 1
			if count > 3:
				break
	if count > 3:
		tags.append('choice')

	teams[team].append({'bias': bias, 'stalliness' : stalliness, 'tags' : tags})

#nickanmes
nicks = []
for i in range(0,6):
	if len(log['p1team'])>i:
		if 'name' in log['p1team'][i].keys():
			nicks.append("p1: "+log['p1team'][i]['name'])
		else:
			nicks.append("p1: "+log['p1team'][i]['species'])
	else:
		nicks.append("p1: empty")
	if len(log['p2team'])>i:
		if 'name' in log['p2team'][i].keys():
			nicks.append("p2: "+log['p2team'][i]['name'])
		else:
			nicks.append("p2: "+log['p2team'][i]['species'])
	else:		
		nicks.append("p1: empty")

#metrics get declared here
turnsOut = [] #turns out on the field (a measure of stall)
KOs = [] #number of KOs in the battle
matchups = [] #poke1, poke2, what happened

for i in range(0,12):
	turnsOut.append(0)
	KOs.append(0)

if 'log' in log.keys():
	#determine initial pokemon
	active = [-1,-1]
	for line in log['log']:
		if (spacelog and line[0:14] == "| switch | p1:") or (not spacelog and line[0:11] == "|switch|p1:"):
			end = string.rfind(line,'|')-1*spacelog
			species = line[string.rfind(line,'|',12+3*spacelog,end-1)+1+1*spacelog:end]
			while ',' in species:
				species = species[0:string.rfind(species,',')]
			active[0]=ts.index([ts[0][0],species])
		if (spacelog and line[0:14] == "| switch | p2:") or (not spacelog and line[0:11] == "|switch|p2:"):
			end = string.rfind(line,'|')-1*spacelog
			species = line[string.rfind(line,'|',12+3*spacelog,end-1)+1+1*spacelog:end]
			while ',' in species:
				species = species[0:string.rfind(species,',')]
			active[1]=ts.index([ts[11][0],species])
			break
	start=log['log'].index(line)+1
		
	#metrics get declared here
	turnsOut = [] #turns out on the field (a measure of stall)
	KOs = [] #number of KOs in the battle
	matchups = [] #poke1, poke2, what happened

	for i in range(0,12):
		turnsOut.append(0)
		KOs.append(0)

	#parse the damn log

	#flags
	roar = False
	uturn = False
	ko = [False,False]
	switch = [False,False]
	uturnko = False
	mtemp = []

	for line in log['log'][start:]:
		#print line
		#identify what kind of message is on this line
		linetype = line[1+1*spacelog:string.find(line,'|',1+1*spacelog)-1*spacelog]

		if linetype == "turn":
			matchups = matchups + mtemp
			mtemp = []

			#reset for start of turn
			roar = uturn = uturnko = False
			ko = [False,False]
			switch = [False,False]

			#Mark each poke as having been out for an additional turn
			turnsOut[active[0]]=turnsOut[active[0]]+1
			turnsOut[active[1]]=turnsOut[active[1]]+1

		elif linetype == "win": 
			#close out last matchup
			if ko[0] or ko[1]: #if neither poke was KOed, match ended in forfeit, and we don't care
				pokes = [ts[active[0]][1],ts[active[1]][1]]
				pokes=sorted(pokes, key=lambda pokes:pokes)
				matchup=pokes[0]+' vs. '+pokes[1]+': '
				if ko[0] and ko[1]:
					KOs[active[0]] = KOs[active[0]]+1
					KOs[active[1]] = KOs[active[1]]+1
					matchup = matchup + "double down"
				else:
					KOs[active[ko[0]]] = KOs[active[ko[0]]]+1
					matchup = matchup + ts[active[ko[1]]][1] + " was "
					if uturnko: #would rather not use this flag...
						mtemp=mtemp[:len(mtemp)-1]
						matchup = matchup + "u-turn "
					matchup = matchup + "KOed"
				mtemp.append(matchup)
			matchups=matchups+mtemp
			

		elif linetype == "move": #check for Roar, etc.; U-Turn, etc.
			#identify attacker and skip its name
			found = False
			for nick in nicks:
				if line[6+3*spacelog:].startswith(nick):
					if found: #the trainer was a d-bag
						if len(nick) < len(found):
							continue	
					found = nick
			tempnicks = copy.copy(nicks)
			while not found: #PS fucked up the names. We fix by shaving a character at a time off the nicknames
				foundidx=-1	
				for i in range(len(tempnicks)):
					if len(tempnicks[i])>1:
						tempnicks[i]=tempnicks[i][:len(tempnicks[i])-1]
					if line[9:].startswith(tempnicks[i]):
						if found:
							if len(tempnicks[i]) < len(found):
								continue	
						found = tempnicks[i]
						foundidx = i
				if found:
					nicks[i]=found
		
			move = line[7+5*spacelog+len(found):string.find(line,"|",7+5*spacelog+len(found))-1*spacelog]
			if move in ["Roar","Whirlwind","Circle Throw","Dragon Tail"]:
				roar = True
			elif move in ["U-Turn","U-turn","Volt Switch","Baton Pass"]:
				uturn = True

		elif linetype == "-enditem": #check for Red Card, Eject Button
			#search for relevant items
			if string.rfind(line,"Red Card") > -1:
				roar = True
			elif string.rfind(line,"Eject Button") > -1:
				uturn = True

		elif linetype == "faint": #KO
			#who fainted?
			ko[int(line[8+3*spacelog])-1]=1

			if uturn:
				uturn=False
				uturnko=True

		elif linetype in ["switch","drag"]: #switch out: new matchup!
			if linetype == "switch":
				p=9+3*spacelog
			else:
				p=7+3*spacelog	
			switch[int(line[p])-1]=True

			if switch[0] and switch[1]: #need to revise previous matchup
				matchup=mtemp[len(mtemp)-1][:string.find(mtemp[len(mtemp)-1],':')+2]
				if (not ko[0]) and (not ko[1]): #double switch
					matchup = matchup + "double switch"
				elif ko[0] and ko[1]: #double down
					KOs[active[ko[0]]] = KOs[active[ko[0]]]+1
					matchup = matchup + "double down"
				else: #u-turn KO (note that this includes hit-by-red-card-and-dies and roar-then-die-by-residual-dmg)
					KOs[active[ko[0]]] = KOs[active[ko[0]]]+1
					matchup = matchup + ts[active[ko[1]]][1]+" was u-turn KOed"
				mtemp[len(mtemp)-1]=matchup
			else:
				#close out old matchup
				pokes = [ts[active[0]][1],ts[active[1]][1]]
				pokes=sorted(pokes, key=lambda pokes:pokes)
				matchup=pokes[0]+' vs. '+pokes[1]+': '
				#if ko[0] and ko[1]: #double down
				if ko[0] or ko[1]:
					KOs[active[ko[0]]] = KOs[active[ko[0]]]+1
					matchup = matchup + ts[active[ko[1]]][1]+" was KOed"
				else:
					matchup = matchup + ts[active[switch[1]]][1]
					if roar:
						matchup = matchup + " was forced out"
					else:
						matchup = matchup + " was switched out"
				mtemp.append(matchup)
		
			#new matchup!
			uturn = roar = 0
			#it matters whether the poke is nicknamed or not
			end = string.rfind(line,'|')-1*spacelog
			species = line[string.rfind(line,'|',12+3*spacelog,end-1)+1+1*spacelog:end]
			while ',' in species:
				species = species[0:string.rfind(species,',')]
			active[int(line[p])-1]=ts.index([ts[11*(int(line[p])-1)][0],species])

#totalTurns = log['turns']
#totalKOs = sum(KOs)

outname = "Raw/"+tier+".txt"
d = os.path.dirname(outname)
if not os.path.exists(d):
	os.makedirs(d)
outfile=open(outname,'a')

teamtags = teams['p1team'][len(teams['p1team'])-1]

outfile.write(ts[0][0].encode('ascii','replace'))
outfile.write(' (bias:'+str(teamtags['bias'])+', stalliness:'+str(teamtags['stalliness'])+', tags:'+','.join(teamtags['tags'])+')')
outfile.write("\n")
i=0
while (ts[i][0] == ts[0][0]):
	outfile.write(ts[i][1]+" ("+str(KOs[i])+","+str(turnsOut[i])+")\n")
	i = i + 1
outfile.write("***\n")
teamtags = teams['p2team'][len(teams['p2team'])-1]
outfile.write(ts[len(ts)-1][0].encode('ascii','replace'))
outfile.write(' (bias:'+str(teamtags['bias'])+', stalliness:'+str(teamtags['stalliness'])+', tags:'+','.join(teamtags['tags'])+')')
outfile.write("\n")
for j in range(i,len(ts)):
	outfile.write(ts[j][1]+" ("+str(KOs[j])+","+str(turnsOut[j])+")\n")
outfile.write("@@@\n")
for line in matchups:
	outfile.write(line+"\n")
outfile.write("---\n")
outfile.close()	

