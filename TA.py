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

file = open('baseStats.json')
baseStats = json.loads(file.readline())
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

def analyzeTeam(team):
	tbias = 0
	tstalliness = []
	for poke in team:
		if poke['species'] not in baseStats.keys():
			sys.stderr.write(poke['species']+" is not listed in baseStats.json\n")
			sys.stderr.write("You may want to fix that.\n")
			sys.exit(1)
		
		if poke['species'] == 'meloetta' and 'relicsong' in poke['moves']:
			poke['species']='meloettapirouette'
		elif poke['species'] == 'darmanitan' and poke['ability'] == 'zenmode':
			poke['species']='darmanitanzen'

		#technically I don't need to do this as a separate loop, but I'm doing it this way for modularity's sake
		stats = []
		if poke['species'] == 'shedinja':
			stats.append(1)
		else:
			stats.append(statFormula(baseStats[poke['species']]['hp'],poke['level'],-1,poke['ivs']['hp'],poke['evs']['hp']))
		stats.append(statFormula(baseStats[poke['species']]['atk'],poke['level'],nmod[poke['nature']][0],poke['ivs']['atk'],poke['evs']['atk']))
		stats.append(statFormula(baseStats[poke['species']]['def'],poke['level'],nmod[poke['nature']][1],poke['ivs']['def'],poke['evs']['def']))
		stats.append(statFormula(baseStats[poke['species']]['spa'],poke['level'],nmod[poke['nature']][3],poke['ivs']['spa'],poke['evs']['spa']))
		stats.append(statFormula(baseStats[poke['species']]['spd'],poke['level'],nmod[poke['nature']][4],poke['ivs']['spd'],poke['evs']['spd']))
		stats.append(statFormula(baseStats[poke['species']]['spe'],poke['level'],nmod[poke['nature']][2],poke['ivs']['spe'],poke['evs']['spe']))

	#calculate base stalliness
		bias = poke['evs']['atk']+poke['evs']['spa']-poke['evs']['hp']-poke['evs']['def']-poke['evs']['spd']
		if poke['species'] == 'shedinja':
			stalliness = 0
		elif poke['species'] == 'ditto':
			stalliness = math.log(3,2) #eventually I'll want to replace this with mean stalliness for the tier
		else:
			stalliness=-math.log(((2.0*poke['level']+10)/250*max(stats[1],stats[3])/max(stats[2],stats[4])*120+2)*0.925/stats[0],2)

		#moveset modifications
		if poke['ability'] in ['purepower','hugepower']:
			stalliness = stalliness - 1.0
		if poke['item'] in ['choiceband','choicescarf','choicespecs','lifeorb']:
			stalliness = stalliness - 0.5
		if poke['item'] == 'eviolite':
			stalliness = stalliness + 0.5
		if 'spikes' in poke['moves']:
			stalliness = stalliness + 0.5
		if 'toxicspikes' in poke['moves']:
			stalliness = stalliness + 0.5
		if 'toxic' in poke['moves']:
			stalliness = stalliness + 1.0
		if 'willowisp' in poke['moves']:
			stalliness = stalliness + 0.5
		if len(set(['recover' ,'slackoff', 'healorder', 'milkdrink', 'roost', 'moonlight', 'morningsun', 'synthesis', 'wish', 'aquaring', 'rest', 'softboiled', 'swallow', 'leechseed']).intersection(poke['moves'])) != 0:
			stalliness = stalliness + 1.0
		if poke['ability'] == 'regenerator':
			stalliness = stalliness + 0.5
		if len(set(['healbell','aromatherapy']).intersection(poke['moves'])) != 0:
			stalliness = stalliness + 0.5
		if poke['ability'] in ['chlorophyll', 'download', 'hustle', 'moxie', 'reckless', 'sandrush', 'solarpower', 'swiftswim', 'technician', 'tintedlens']:
			stalliness = stalliness - 0.5
		if poke['ability'] in ['flareboost', 'guts', 'quickfeet'] and poke['item'] == 'flameorb':
			stalliness = stalliness - 1.0
		if poke['ability'] in ['toxicboost', 'guts', 'quickfeet'] and poke['item'] == 'toxicorb':
			stalliness = stalliness - 1.0
		if poke['ability'] in ['speedboost', 'moody']:
			stalliness = stalliness - 1.0
		if poke['ability'] in ['arenatrap','magnetpull','shadowtag']:
			stalliness = stalliness - 1.0
		elif len(set(['block','meanlook','spiderweb','pursuit']).intersection(poke['moves'])) != 0:
			stalliness = stalliness - 0.5
		if poke['ability'] in ['dryskin', 'filter', 'hydration', 'icebody', 'intimidate', 'ironbarbs', 'marvelscale', 'naturalcure', 'magicguard', 'multiscale', 'raindish', 'roughskin', 'solidrock', 'thickfat', 'unaware']:
			stalliness = stalliness + 0.5
		if poke['ability'] == 'poisonheal' and poke['item'] == 'toxicorb':
			stalliness = stalliness + 0.5
		if poke['ability'] in ['slowstart','truant']:
			stalliness = stalliness + 1.0
		if poke['item'] == 'lightclay':
			stalliness = stalliness - 1.0
		if 'bellydrum' in poke['moves']:
			stalliness = stalliness - 2.0
		elif 'shellsmash' in poke['moves']:
			stalliness = stalliness - 1.5
		elif len(set(['curse', 'dragondance', 'growth', 'shiftgear', 'swordsdance', 'fierydance', 'nastyplot', 'tailglow', 'quiverdance']).intersection(poke['moves'])) != 0:
			stalliness = stalliness - 1.0
		elif len(set(['acupressure', 'bulkup', 'coil', 'howl', 'workup', 'meditate', 'sharpen', 'calmmind', 'chargebeam', 'agility', 'autotomize', 'flamecharge', 'rockpolish', 'doubleteam', 'minimize', 'tailwind']).intersection(poke['moves'])) != 0:
			stalliness = stalliness - 0.5
		if 'substitute' in poke['moves']:
			stalliness = stalliness - 0.5
		if 'protect' in poke['moves'] or 'detect' in poke['moves']:
			stalliness = stalliness + 1.0
		if 'endeavor' in poke['moves']:
			stalliness = stalliness - 1.0
		if 'superfang' in poke['moves']:
			stalliness = stalliness - 0.5
		if 'trick' in poke['moves']:
			stalliness = stalliness - 0.5
		if 'psychoshift' in poke['moves']:
			stalliness = stalliness + 0.5
		if len(set(['whirlwind', 'roar', 'circlethrow', 'dragontail']).intersection(poke['moves'])) != 0:
			stalliness = stalliness + 0.5
		if len(set(['haze', 'clearsmog']).intersection(poke['moves'])) != 0:
			stalliness = stalliness + 0.5
		if len(set(['thunderwave', 'stunspore', 'glare']).intersection(poke['moves'])) != 0:
			stalliness = stalliness + 0.5
		if len(set(['supersonic', 'confuseray', 'swagger', 'flatter', 'teeterdance', 'yawn']).intersection(poke['moves'])) != 0:
			stalliness = stalliness + 0.5
		if len(set(['darkvoid', 'grasswhistle', 'hypnosis', 'lovelykiss', 'sing', 'sleeppowder', 'spore']).intersection(poke['moves'])) != 0:
			stalliness = stalliness - 0.5
		if poke['item'] == 'redcard':
			stalliness = stalliness + 0.5
		if poke['item'] == 'rockyhelmet':
			stalliness = stalliness + 0.5
		if poke['item'] in ['firegem', 'watergem', 'electricgem', 'grassgem', 'icegem', 'fightinggem', 'posiongem', 'groundgem', 'groundgem', 'flyinggem', 'psychicgem', 'buggem', 'rockgem', 'ghostgem', 'darkgem', 'steelgem', 'normalgem', 'focussash', 'mentalherb', 'powerherb', 'whiteherb', 'absorbbulb', 'berserkgene', 'cellbattery', 'redcard', 'focussash', 'airballoon', 'ejectbutton', 'shedshell', 'aguavberry', 'apicotberry', 'aspearberry', 'babiriberry', 'chartiberry', 'cheriberry', 'chestoberry', 'chilanberry', 'chopleberry', 'cobaberry', 'custapberry', 'enigmaberry', 'figyberry', 'ganlonberry', 'habanberry', 'iapapaberry', 'jabocaberry', 'kasibberry', 'kebiaberry', 'lansatberry', 'leppaberry', 'liechiberry', 'lumberry', 'magoberry', 'micleberry', 'occaberry', 'oranberry', 'passhoberry', 'payapaberry', 'pechaberry', 'persimberry', 'petayaberry', 'rawstberry', 'rindoberry', 'rowapberry', 'salacberry', 'shucaberry', 'sitrusberry', 'starfberry', 'tangaberry', 'wacanberry', 'wikiberry', 'yacheberry']:
			stalliness = stalliness - 0.5
		if poke['ability'] == 'harvest' or 'recycle' in poke['moves']:
			stalliness = stalliness + 1
		#if len(set(['jumpkick', 'doubleedge', 'submission', 'petaldance', 'hijumpkick', 'outrage', 'superpower', 'overheat', 'volttackle', 'psychoboost', 'hammerarm', 'closecombat', 'flareblitz', 'bravebird', 'dracometeor', 'leafstorm', 'woodhammer', 'headsmash', 'headcharge', 'vcreate', 'wildcharge', 'takedown']).intersection(poke['moves'])) != 0:
		if len(set(['jumpkick', 'doubleedge', 'submission', 'petaldance', 'hijumpkick', 'outrage', 'volttackle', 'closecombat', 'flareblitz', 'bravebird', 'woodhammer', 'headsmash', 'headcharge', 'wildcharge', 'takedown']).intersection(poke['moves'])) != 0:
			stalliness = stalliness - 0.5
		if len(set(['selfdestruct', 'explosion', 'destinybond', 'perishsong', 'memento', 'healingwish', 'lunardance', 'finalgambit']).intersection(poke['moves'])) != 0:
			stalliness = stalliness - 1.0
		if len(set(['guillotine', 'fissure', 'sheercold']).intersection(poke['moves'])) != 0:
			stalliness = stalliness - 1.0
		if poke['ability'] in ['sandstream','snowwarning'] or 'sandstorm' in poke['moves'] or 'hail' in poke['moves']:
			stalliness = stalliness + 0.5
		if poke['species'] in ['latios', 'latias'] and poke['item'] == 'souldew':
			stalliness = stalliness - 0.5
		if poke['species'] == 'pikachu' and poke['item'] == 'lightball':
			stalliness = stalliness - 1.0
		if poke['species'] in ['cubone', 'marowak'] and poke['item'] == 'thickclub':
			stalliness = stalliness - 1.0
		if poke['species'] == 'clamperl' and poke['item'] == 'deepseatooth':
			stalliness = stalliness - 1.0
		if poke['species'] == 'clamperl' and poke['item'] == 'deepseascale':
			stalliness = stalliness + 1.0
		if poke['item'] in ['expertbelt', 'wiseglasses', 'muscleband', 'dracoplate', 'dreadplate', 'earthplate', 'fistplate', 'flameplate', 'icicleplate', 'insectplate', 'ironplate', 'meadowplate', 'mindplate', 'skyplate', 'splashplate', 'spookyplate', 'stoneplate', 'toxicplate', 'zapplate', 'blackglasses', 'charcoal', 'dragonfang', 'hardstone', 'magnet', 'metalcoat', 'miracleseed', 'mysticwater', 'nevermeltice', 'poisonbarb', 'sharpbeak', 'silkscarf', 'silverpowder', 'softsand', 'spelltag', 'twistedspoon']:
			stalliness = stalliness - 0.25
		if poke['species'] == 'dialga' and poke['item'] == 'adamantorb':
			stalliness = stalliness - 0.25
		if poke['species'] == 'palkia' and poke['item'] == 'lustrousorb':
			stalliness = stalliness - 0.25
		if poke['species'] == 'giratinaorigin' and poke['item'] == 'griseousorb': #it's better be holding a Griseous Orb
			stalliness = stalliness - 0.25
		#if poke['item'] == 'leftovers':
		#	stalliness = stalliness + 0.25

		#final correction
		stalliness=stalliness-math.log(3,2)

		tbias = tbias + bias
		#tstalliness = tstalliness + stalliness
		tstalliness.append(stalliness)

	#team-type detection
	#tstalliness=sorted(tstalliness, key=lambda tstalliness:tstalliness)
	#allsix=sum(tstalliness)/len(tstalliness)
	#topfive=sum(tstalliness[1:])/(len(tstalliness)-1)
	#bottomfive=sum(tstalliness[:len(tstalliness)-1])/(len(tstalliness)-1)
	#if topfive-allsix > allsix-bottomfive:
	#	tstalliness=topfive
	#else:
	#	tstalliness=bottomfive
	tstalliness = sum(tstalliness) / len(tstalliness)
	tags = []	

	#don't put anything before weather

	#rain
	count = 0
	detected = False
	for poke in team:
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
	for poke in team:
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
	for poke in team:
		if 'batonpass' in poke['moves']:
			if len(set(['acupressure', 'bellydrum', 'bulkup', 'coil', 'curse', 'dragondance', 'growth', 'honeclaws', 'howl', 'meditate', 'sharpen', 'shellsmash', 'shiftgear', 'swordsdance', 'workup', 'calmmind', 'chargebeam', 'fierydance', 'nastyplot', 'tailglow', 'quiverdance', 'agility', 'autotomize', 'flamecharge', 'rockpolish', 'doubleteam', 'minimize', 'substitute', 'acidarmor', 'barrier', 'cosmicpower', 'cottonguard', 'defendorder', 'defensecurl', 'harden', 'irondefense', 'stockpile', 'withdraw', 'amnesia', 'charge', 'ingrain']).intersection(poke['moves'])) != 0 or poke['ability'] in ['angerpoint', 'contrary', 'moody', 'moxie', 'speedboost']: #check for setup move/ability
				count = count + 1
				if count > 1:
					break
	if count > 1:
		tags.append('batonpass')

	#trick room
	count = [0,0]

	for poke in team:
		if 'trickroom' in poke['moves'] and 'imprison' not in poke['moves']:
			count[0] = count[0] + 1
		elif (poke['nature'] in ['brave', 'relaxed', 'quiet', 'sassy'] or baseStats[poke['species']]['spe'] <= 50) and poke['evs']['spe'] < 5: #or I could just use actual stats and speed factor
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

	for poke in team:
		if 'gravity' in poke['moves']:
			count[0] = count[0] + 1
		if len(set(['guillotine', 'fissure', 'sheercold', 'dynamicpunch', 'inferno', 'zapcannon', 'grasswhistle', 'sing', 'supersonic', 'hypnosis', 'blizzard', 'focusblast', 'gunkshot', 'hurricane', 'smog', 'thunder', 'clamp', 'dragonrush', 'eggbomb', 'irontail', 'lovelykiss', 'magmastorm', 'megakick', 'poisonpowder', 'slam', 'sleeppowder', 'stunspore', 'sweetkiss', 'willowisp', 'crosschop', 'darkvoid', 'furyswipes', 'headsmash', 'hydropump', 'kinesis', 'psywave', 'rocktomb', 'stoneedge', 'submission', 'boneclub', 'bonerush', 'bonemerang', 'bulldoze', 'dig', 'drillrun', 'earthpower', 'earthquake', 'magnitude', 'mudbomb', 'mudshot', 'mudslap', 'sandattack', 'spikes', 'toxicspikes']).intersection(poke['moves'])) != 0:
			count[1] = count[1] + 1

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
			count[0] = count[0] + 1
		elif poke['species'] in ['dratini', 'dragonair', 'bagon', 'shelgon', 'axew', 'fraxure', 'haxorus', 'druddigon', 'dragonite', 'altaria', 'salamence', 'latias', 'latios', 'rayquaza', 'gible', 'gabite', 'garchomp', 'reshiram', 'zekrom', 'kyurem', 'kyuremwhite', 'kyuremblack', 'kingdra', 'vibrava', 'flygon', 'dialga', 'palkia', 'giratina', 'giratinaorigin', 'deino', 'zweilous', 'hydreigon']:
			count[1] = count[1] + 1
	if count[0] > 0 and count[1] > 1:
		tags.append('dragmag')
	if count[0] > 2:
		tags.append('trapper')

	#F.E.A.R.
	count = [0,0]

	for poke in team:
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

	for poke in team:
		if poke['item'] in ['choiceband', 'choicescarf', 'choicespecs'] and poke['ability'] != 'klutz':
			count = count + 1
			if count > 3:
				break
	if count > 3:
		tags.append('choice')

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

