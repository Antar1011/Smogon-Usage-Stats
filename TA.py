#!/usr/bin/python
#This file contains the analyzeTeam function, which returns bias, stalliness and team tags for an inputted team.
#The format required for the team is fairly specific. I would not recommend trying to directly create a team yourself.
#Instead, look at TeamAnalyzer.py for an example of how to take a plaintext PO/PS export ("importable") and convert it
#to the format requred by this function. Alternately, if you have access to PS server-side json logs, look at LogReader.py
#to see how to read in teams from those logs.

import string
import sys
import json
import math
import copy
from common import keyify

file = open('baseStats.json')
baseStats = json.loads(file.readline())
file.close()

file = open('types.json')
types = json.loads(file.readline())
file.close()

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
	
megas=[	['abomasnow','abomasite','snowwarning'],
	['absol','absolite','magicbounce'],
	['aerodactyl','aerodactylite','toughclaws'],
	['aggron','aggronite','filter'],
	['alakazam','alakazite','trace'],
	['altaria','altarianite','pixilate'],
	['ampharos','ampharosite','moldbreaker'],
	['audino','audinite','healer'],
	['banette','banettite','prankster'],
	['beedrill','beedrillite','adaptability'],
	['blastoise','blastoisinite','megalauncher'],
	['blaziken','blazikenite','speedboost'],
	['camerupt','cameruptite','sheerforce'],
	['charizard','charizarditex','toughclaws'],
	['charizard','charizarditey','drought'],
	['diancie','diancite','magicbounce'],
	['gallade','galladite','innerfocus'],
	['garchomp','garchompite','sandforce'],
	['gardevoir','gardevoirite','pixilate'],
	['gengar','gengarite','shadowtag'],
	['glalie','glalitite','refrigerate'],
	['gyarados','gyaradosite','moldbreaker'],
	['heracross','heracronite','skilllink'],
	['houndoom','houndoominite','solarpower'],
	['kangaskhan','kangaskhanite','parentalbond'],
	['latias','latiasite','levitate'],
	['latios','latiosite','levitate'],
	['lopunny','lopunnite','scrappy'],
	['lucario','lucarionite','adaptability'],
	['manectric','manectite','intimidate'],
	['mawile','mawilite','hugepower'],
	['medicham','medichamite','purepower'],
	['metagross','metagrossite','toughclaws'],
	['mewtwo','mewtwonitex','steadfast'],
	['mewtwo','mewtwonitey','insomnia'],
	['pidgeot','pidgeotite','noguard'],
	['pinsir','pinsirite','aerilate'],
	['sableye','sablenite','magicbounce'],
	['salamence','salamencite','aerilate'],
	['sceptile','sceptilite','lightningrod'],
	['scizor','scizorite','technician'],
	['sharpedo','sharpedonite','strongjaw'],
	['slowbro','slowbronite','shellarmor'],
	['steelix','steelixite','sandforce'],
	['swampert','swampertite','swiftswim'],
	['tyranitar','tyranitarite','sandstream'],
	['venusaur','venusaurite','thickfat'],
	['kyogre','blueorb','primordialsea'],
	['groudon','redorb','desolateland'],
	['crucibelle','crucibellite','magicguard']]
	
def analyzePoke(poke):
	species=keyify(poke['species'])
	if species not in baseStats.keys():
		sys.stderr.write(species+" is not listed in baseStats.json\n")
		sys.stderr.write("You may want to fix that.\n")
		return None	

	#technically I don't need to do this as a separate loop, but I'm doing it this way for modularity's sake
	stats = []
	if species == 'shedinja':
		stats.append(1)
	else:
		stats.append(statFormula(baseStats[species]['hp'],poke['level'],-1,poke['ivs']['hp'],poke['evs']['hp']))
	stats.append(statFormula(baseStats[species]['atk'],poke['level'],nmod[poke['nature']][0],poke['ivs']['atk'],poke['evs']['atk']))
	stats.append(statFormula(baseStats[species]['def'],poke['level'],nmod[poke['nature']][1],poke['ivs']['def'],poke['evs']['def']))
	stats.append(statFormula(baseStats[species]['spa'],poke['level'],nmod[poke['nature']][3],poke['ivs']['spa'],poke['evs']['spa']))
	stats.append(statFormula(baseStats[species]['spd'],poke['level'],nmod[poke['nature']][4],poke['ivs']['spd'],poke['evs']['spd']))
	stats.append(statFormula(baseStats[species]['spe'],poke['level'],nmod[poke['nature']][2],poke['ivs']['spe'],poke['evs']['spe']))

	if species == 'aegislash' and poke['ability'] == 'stancechange': #check for attacking move as well?
		stats[1] =  statFormula(baseStats['aegislashblade']['atk'],poke['level'],nmod[poke['nature']][0],poke['ivs']['atk'],poke['evs']['atk'])
		stats[2] += statFormula(baseStats['aegislashblade']['def'],poke['level'],nmod[poke['nature']][1],poke['ivs']['def'],poke['evs']['def'])
		stats[3] =  statFormula(baseStats['aegislashblade']['spa'],poke['level'],nmod[poke['nature']][3],poke['ivs']['spa'],poke['evs']['spa'])
		stats[4] += statFormula(baseStats['aegislashblade']['spd'],poke['level'],nmod[poke['nature']][4],poke['ivs']['spd'],poke['evs']['spd'])
		stats[2] /= 2
		stats[4] /= 2

	#calculate base stalliness
	bias = poke['evs']['atk']+poke['evs']['spa']-poke['evs']['hp']-poke['evs']['def']-poke['evs']['spd']
	if species == 'shedinja':
		stalliness = 0
	elif species == 'ditto':
		stalliness = math.log(3,2) #eventually I'll want to replace this with mean stalliness for the tier
	else:
		try:
			stalliness=-math.log(((2.0*poke['level']+10)/250*max(stats[1],stats[3])/max(stats[2],stats[4])*120+2)*0.925/stats[0],2)
		except:
			sys.stderr.write('Got a problem with a '+species+'\n')
			sys.stderr.write(poke)
			return None

	#moveset modifications
	if poke['ability'] in ['purepower','hugepower']:
		stalliness -= 1.0
	if poke['item'] in ['choiceband','choicescarf','choicespecs','lifeorb']:
		stalliness -= 0.5
	if poke['item'] == 'eviolite':
		stalliness += 0.5
	if 'spikes' in poke['moves']:
		stalliness += 0.5
	if 'toxicspikes' in poke['moves']:
		stalliness += 0.5
	if 'toxic' in poke['moves']:
		stalliness += 1.0
	if 'willowisp' in poke['moves']:
		stalliness += 0.5
	if len(set(['recover' ,'slackoff', 'healorder', 'milkdrink', 'roost', 'moonlight', 'morningsun', 'synthesis', 'wish', 'aquaring', 'rest', 'softboiled', 'swallow', 'leechseed']).intersection(poke['moves'])) != 0:
		stalliness += 1.0
	if poke['ability'] == 'regenerator':
		stalliness += 0.5
	if len(set(['healbell','aromatherapy']).intersection(poke['moves'])) != 0:
		stalliness += 0.5
	if poke['ability'] in ['chlorophyll', 'download', 'hustle', 'moxie', 'reckless', 'sandrush', 'solarpower', 'swiftswim', 'technician', 'tintedlens', 'darkaura', 'fairyaura', 'infiltrator', 'parentalbond', 'protean', 'strongjaw', 'sweetveil', 'toughclaws','aerilate','normalize','pixilate','refrigerate']:
		stalliness -= 0.5
	if poke['ability'] in ['flareboost', 'guts', 'quickfeet'] and poke['item'] == 'flameorb':
		stalliness -= 1.0
	if poke['ability'] in ['toxicboost', 'guts', 'quickfeet'] and poke['item'] == 'toxicorb':
		stalliness -= 1.0
	if poke['ability'] in ['speedboost', 'moody']:
		stalliness -= 1.0
	if poke['ability'] in ['arenatrap','magnetpull','shadowtag']:
		stalliness -= 1.0
	elif len(set(['block','meanlook','spiderweb','pursuit']).intersection(poke['moves'])) != 0:
		stalliness -= 0.5
	if poke['ability'] in ['dryskin', 'filter', 'hydration', 'icebody', 'intimidate', 'ironbarbs', 'marvelscale', 'naturalcure', 'magicguard', 'multiscale', 'raindish', 'roughskin', 'solidrock', 'thickfat', 'unaware', 'aromaveil', 'bulletproof', 'cheekpouch', 'gooey']:
		stalliness += 0.5
	if poke['ability'] == 'poisonheal' and poke['item'] == 'toxicorb':
		stalliness += 0.5
	if poke['ability'] in ['slowstart','truant','furcoat']:
		stalliness += 1.0
	if poke['item'] == 'lightclay':
		stalliness -= 1.0
	if 'bellydrum' in poke['moves']:
		stalliness -= 2.0
	elif 'shellsmash' in poke['moves']:
		stalliness -= 1.5
	elif len(set(['curse', 'dragondance', 'growth', 'shiftgear', 'swordsdance', 'fierydance', 'nastyplot', 'tailglow', 'quiverdance', 'geomancy']).intersection(poke['moves'])) != 0:
		stalliness -= 1.0
	elif len(set(['acupressure', 'bulkup', 'coil', 'howl', 'workup', 'meditate', 'sharpen', 'calmmind', 'chargebeam', 'agility', 'autotomize', 'flamecharge', 'rockpolish', 'doubleteam', 'minimize', 'tailwind', 'poweruppunch', 'rototiller']).intersection(poke['moves'])) != 0:
		stalliness -= 0.5
	if 'substitute' in poke['moves']:
		stalliness -= 0.5
	if len(set(['protect','detect','kingsshield','matblock','spikyshield']).intersection(poke['moves'])) != 0:
		stalliness += 1.0
	if 'endeavor' in poke['moves']:
		stalliness -= 1.0
	if 'superfang' in poke['moves']:
		stalliness -= 0.5
	if 'trick' in poke['moves']:
		stalliness -= 0.5
	if 'psychoshift' in poke['moves']:
		stalliness += 0.5
	if len(set(['whirlwind', 'roar', 'circlethrow', 'dragontail']).intersection(poke['moves'])) != 0:
		stalliness += 0.5
	if len(set(['haze', 'clearsmog']).intersection(poke['moves'])) != 0:
		stalliness += 0.5
	if len(set(['thunderwave', 'stunspore', 'glare', 'nuzzle']).intersection(poke['moves'])) != 0:
		stalliness += 0.5
	if len(set(['supersonic', 'confuseray', 'swagger', 'flatter', 'teeterdance', 'yawn']).intersection(poke['moves'])) != 0:
		stalliness += 0.5
	if len(set(['darkvoid', 'grasswhistle', 'hypnosis', 'lovelykiss', 'sing', 'sleeppowder', 'spore']).intersection(poke['moves'])) != 0:
		stalliness -= 0.5
	if poke['item'] == 'redcard':
		stalliness += 0.5
	if poke['item'] == 'rockyhelmet':
		stalliness += 0.5
	if poke['item'] in ['firegem', 'watergem', 'electricgem', 'grassgem', 'icegem', 'fightinggem', 'posiongem', 'groundgem', 'groundgem', 'flyinggem', 'psychicgem', 'buggem', 'rockgem', 'ghostgem', 'darkgem', 'steelgem', 'normalgem', 'focussash', 'mentalherb', 'powerherb', 'whiteherb', 'absorbbulb', 'berserkgene', 'cellbattery', 'redcard', 'focussash', 'airballoon', 'ejectbutton', 'shedshell', 'aguavberry', 'apicotberry', 'aspearberry', 'babiriberry', 'chartiberry', 'cheriberry', 'chestoberry', 'chilanberry', 'chopleberry', 'cobaberry', 'custapberry', 'enigmaberry', 'figyberry', 'ganlonberry', 'habanberry', 'iapapaberry', 'jabocaberry', 'kasibberry', 'kebiaberry', 'lansatberry', 'leppaberry', 'liechiberry', 'lumberry', 'magoberry', 'micleberry', 'occaberry', 'oranberry', 'passhoberry', 'payapaberry', 'pechaberry', 'persimberry', 'petayaberry', 'rawstberry', 'rindoberry', 'rowapberry', 'salacberry', 'shucaberry', 'sitrusberry', 'starfberry', 'tangaberry', 'wacanberry', 'wikiberry', 'yacheberry','keeberry','marangaberry','roseliberry','snowball']:
		stalliness -= 0.5
	if poke['ability'] == 'harvest' or 'recycle' in poke['moves']:
		stalliness += 1.0
	if len(set(['jumpkick', 'doubleedge', 'submission', 'petaldance', 'hijumpkick', 'outrage', 'volttackle', 'closecombat', 'flareblitz', 'bravebird', 'woodhammer', 'headsmash', 'headcharge', 'wildcharge', 'takedown', 'dragonascent']).intersection(poke['moves'])) != 0:
		stalliness -= 0.5
	if len(set(['selfdestruct', 'explosion', 'destinybond', 'perishsong', 'memento', 'healingwish', 'lunardance', 'finalgambit']).intersection(poke['moves'])) != 0:
		stalliness -= 1.0
	if len(set(['guillotine', 'fissure', 'sheercold']).intersection(poke['moves'])) != 0:
		stalliness -= 1.0
	if poke['ability'] in ['sandstream','snowwarning'] or 'sandstorm' in poke['moves'] or 'hail' in poke['moves']:
		stalliness += 0.5
	if species in ['latios', 'latias'] and poke['item'] == 'souldew':
		stalliness -= 0.5
	if species == 'pikachu' and poke['item'] == 'lightball':
		stalliness -= 1.0
	if species in ['cubone', 'marowak'] and poke['item'] == 'thickclub':
		stalliness -= 1.0
	if species == 'clamperl' and poke['item'] == 'deepseatooth':
		stalliness -= 1.0
	if species == 'clamperl' and poke['item'] == 'deepseascale':
		stalliness += 1.0
	if poke['item'] in ['expertbelt', 'wiseglasses', 'muscleband', 'dracoplate', 'dreadplate', 'earthplate', 'fistplate', 'flameplate', 'icicleplate', 'insectplate', 'ironplate', 'meadowplate', 'mindplate', 'skyplate', 'splashplate', 'spookyplate', 'stoneplate', 'toxicplate', 'zapplate', 'blackglasses', 'charcoal', 'dragonfang', 'hardstone', 'magnet', 'metalcoat', 'miracleseed', 'mysticwater', 'nevermeltice', 'poisonbarb', 'sharpbeak', 'silkscarf', 'silverpowder', 'softsand', 'spelltag', 'twistedspoon', 'pixieplate']:
		stalliness -= 0.25
	if species == 'dialga' and poke['item'] == 'adamantorb':
		stalliness -= 0.25
	if species == 'palkia' and poke['item'] == 'lustrousorb':
		stalliness = stalliness - 0.25
	if species == 'giratinaorigin' and poke['item'] == 'griseousorb': #it's better be holding a Griseous Orb
		stalliness -= 0.25
	if poke['item'] == 'weaknesspolicy':
		stalliness -= 1.0
	
	return stalliness,bias

def analyzeTeam(team):
	tbias = 0
	tstalliness = []
	possibleTypes = False

	for p in team:

		#for stats and moveset purposes, we're now counting mega Pokemon separately. But for Team Analysis, we still want to
		#consider the base (this presumably breaks for hackmons, but w/e--hackmons has always been broken)
		poke = copy.deepcopy(p)
		if poke['species'].endswith('-Mega') or poke['species'].endswith('-Mega-X') or poke['species'].endswith('-Mega-Y') or poke['species'].endswith('-Primal'):
			poke['species'] = poke['species'][:poke['species'].index('-')] #none of the megas have hyphenated names

		species = keyify(poke['species'])

		if possibleTypes == False:
			possibleTypes = set(types[species])
		else:
			possibleTypes = possibleTypes.intersection(types[species])
		analysis = analyzePoke(poke)
		if analysis is None:
			return None
		(stalliness,bias) = analysis 
		if species == 'meloetta' and 'relicsong' in poke['moves']:
			megapoke = copy.deepcopy(poke)
			megaspecies='meloettapirouette'
			stalliness += analyzePoke(megapoke)[0]
			stalliness /= 2.0
		elif species == 'darmanitan' and poke['ability'] == 'zenmode':
			megapoke = copy.deepcopy(poke)
			megaspecies='darmanitanzen'
			stalliness += analyzePoke(megapoke)[0]
			stalliness /= 2.0
		elif species == 'rayquaza' and 'dragonascent' in poke['moves']:
			megapoke = copy.deepcopy(poke)
			megaspecies='rayquazamega'
			megapoke['ability']='deltastream'
			stalliness += analyzePoke(megapoke)[0]
			stalliness /= 2.0
		else:
			for mega in megas:
				if [species,poke['item']] == mega[:2]:
					megaspecies = species+'mega'
					if poke['item'].endswith('x'):
						megaspecies +='x'
					elif poke['item'].endswith('y'):
						megaspecies += 'y'
					if megaspecies in ['kyogremega','groudonmega']:
						megaspecies=megaspecies[:-4]+'primal'
					megapoke = copy.deepcopy(poke)
					megaspecies=megaspecies
					megapoke['ability']=mega[2]
					stalliness += analyzePoke(megapoke)[0]
					stalliness /= 2.0
					break

		#final correction
		stalliness=stalliness-math.log(3,2)

		tbias = tbias + bias
		#tstalliness = tstalliness + stalliness
		tstalliness.append(stalliness)

	#team-type detection
	tstalliness = sum(tstalliness) / len(tstalliness)
	tags = []	

	#don't put anything before weather

	#rain
	count = 0
	detected = False
	for poke in team:
		if poke['ability'] in ['drizzle','primordialsea']:
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
	for poke in team:
		if poke['ability'] in ['drought','desolateland']:
			detected = True
			break
		elif [species,poke['item']] == ['charizard','charizarditey']:
			detected = True
			break
		elif poke['item'] == 'heatrock' and 'sunnyday' in poke['moves']:
			detected = True
			break
		elif 'sunnyday' in poke['moves']:
			count += 1
			if count > 1:
				detected = True
				break
	if detected:
		tags.append('sun')

	#sand
	count = 0
	detected = False
	for poke in team:
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
	for poke in team:
		if poke['ability'] == 'snowwarning':
			detected = True
			break
		elif poke['item'] == 'icyrock' and 'hail' in poke['moves']:
			detected = True
			break
		elif 'hail' in poke['moves']:
			count += 1
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
	for poke in team:
		if 'batonpass' in poke['moves']:
			if len(set(['acupressure', 'bellydrum', 'bulkup', 'coil', 'curse', 'dragondance', 'growth', 'honeclaws', 'howl', 'meditate', 'sharpen', 'shellsmash', 'shiftgear', 'swordsdance', 'workup', 'calmmind', 'chargebeam', 'fierydance', 'nastyplot', 'tailglow', 'quiverdance', 'agility', 'autotomize', 'flamecharge', 'rockpolish', 'doubleteam', 'minimize', 'substitute', 'acidarmor', 'barrier', 'cosmicpower', 'cottonguard', 'defendorder', 'defensecurl', 'harden', 'irondefense', 'stockpile', 'withdraw', 'amnesia', 'charge', 'ingrain']).intersection(poke['moves'])) != 0 or poke['ability'] in ['angerpoint', 'contrary', 'moody', 'moxie', 'speedboost']: #check for setup move/ability
				count += 1
				if count > 1:
					break
	if count > 1:
		tags.append('batonpass')

	#tailwind
	count = 0
	for poke in team:
		if 'tailwind' in poke['moves']:
			count += 1
			if count > 1:
				break
	if count > 1:
		tags.append('tailwind')

	#trick room
	count = [0,0]

	for poke in team:
		if 'trickroom' in poke['moves'] and 'imprison' not in poke['moves']:
			count[0] += 1
		elif (poke['nature'] in ['brave', 'relaxed', 'quiet', 'sassy'] or baseStats[species]['spe'] <= 50) and poke['evs']['spe'] < 5: #or I could just use actual stats and speed factor
			count[1] += 1

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

	for poke in team:
		if 'gravity' in poke['moves']:
			count[0] += 1
		if len(set(['guillotine', 'fissure', 'sheercold', 'dynamicpunch', 'inferno', 'zapcannon', 'grasswhistle', 'sing', 'supersonic', 'hypnosis', 'blizzard', 'focusblast', 'gunkshot', 'hurricane', 'smog', 'thunder', 'clamp', 'dragonrush', 'eggbomb', 'irontail', 'lovelykiss', 'magmastorm', 'megakick', 'poisonpowder', 'slam', 'sleeppowder', 'stunspore', 'sweetkiss', 'willowisp', 'crosschop', 'darkvoid', 'furyswipes', 'headsmash', 'hydropump', 'kinesis', 'psywave', 'rocktomb', 'stoneedge', 'submission', 'boneclub', 'bonerush', 'bonemerang', 'bulldoze', 'dig', 'drillrun', 'earthpower', 'earthquake', 'magnitude', 'mudbomb', 'mudshot', 'mudslap', 'sandattack', 'spikes', 'toxicspikes']).intersection(poke['moves'])) != 0:
			count[1] += 1

	if (count[0] > 1 and count[1] > 1) or (count[0] > 2):
		 tags.append('gravity')

	#voltturn
	count = 0

	for poke in team:
		if len(set(['voltswitch','uturn','batonpass']).intersection(poke['moves'])) != 0 or poke['item'] == 'ejectbutton':
			count = count + 1
			if count > 2:
				break
	if count > 2 and 'batonpass' not in tags:
		tags.append('voltturn')

	#dragmag and trapper
	count = [0,0]

	for poke in team:
		if poke['ability'] in ['magnetpull', 'arenatrap', 'shadowtag'] or len(set(['block','meanlook','spiderweb']).intersection(poke['moves'])) != 0:
			count[0] += 1
		elif species in ['dratini', 'dragonair', 'bagon', 'shelgon', 'axew', 'fraxure', 'haxorus', 'druddigon', 'dragonite', 'altaria', 'salamence', 'latias', 'latios', 'rayquaza', 'gible', 'gabite', 'garchomp', 'reshiram', 'zekrom', 'kyurem', 'kyuremwhite', 'kyuremblack', 'kingdra', 'vibrava', 'flygon', 'dialga', 'palkia', 'giratina', 'giratinaorigin', 'deino', 'zweilous', 'hydreigon']:
			count[1] += 1
	if count[0] > 0 and count[1] > 1:
		tags.append('dragmag')
	if count[0] > 2:
		tags.append('trapper')

	#F.E.A.R.
	count = [0,0]

	for poke in team:
		if poke['ability'] == 'magicbounce' or 'rapidspin' in poke['moves']:
			count[0] += 1
		elif (poke['ability'] == 'sturdy' or poke['item'] == 'focussash') and 'endeavor' in poke['moves']:
			count[1] += 1
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

	for poke in team:
		if poke['item'] in ['choiceband', 'choicescarf', 'choicespecs'] and poke['ability'] != 'klutz':
			count += 1
			if count > 3:
				break
	if count > 3:
		tags.append('choice')

	count = 0
	
	for poke in team:
		if len(set(['foulplay','swagger']).intersection(poke['moves'])) > 1:
			count += 1
			if count > 1:
				break
	if count > 1:
		tags.append('swagplay')
		
	#monotype
	possibleTypes = list(possibleTypes)
	if possibleTypes:
		tags.append("monotype")
		for monotype in possibleTypes:
			tags.append('mono'+monotype.lower())

	#stalliness stuff
	if tstalliness <= -1.0:
		tags.append('hyperoffense')
		if 'multiweather' not in tags and 'allweather' not in tags and 'weatherless' not in tags:
			if 'rain' in tags:
				tags.append('rainoffense')
			elif 'sun' in tags:
				tags.append('sunoffense')
			elif 'sand' in tags:
				tags.append('sandoffense')
			else:
				tags.append('hailoffense')
	elif tstalliness <= 0.0:
		tags.append('offense')
	elif tstalliness <= 1.0:
		tags.append('balance')
	elif tstalliness <= math.log(3.0,2.0):
		tags.append('semistall')
	else:
		tags.append('stall')
		if 'multiweather' not in tags and 'allweather' not in tags and 'weatherless' not in tags:
			if 'rain' in tags:
				tags.append('rainstall')
			elif 'sun' in tags:
				tags.append('sunstall')
			elif 'sand' in tags:
				tags.append('sandstall')
			else:
				tags.append('hailstall')

	return {'bias':tbias, 'stalliness': tstalliness, 'tags': tags}

