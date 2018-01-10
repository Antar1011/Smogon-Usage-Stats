#!/usr/bin/python
# -*- coding: latin-1 -*-
#File I/O is going to be the main bottleneck. Doing log reading in batch (a folder at a time, rather than log by log)
#should be much more efficient, as TA.py and the files it requires need only be loaded once per run.

import string
import sys
import ujson as json
import gzip
import copy
#import cPickle as pickle
import math
import os
import ladderdev.Glicko as Glicko
import cPickle as pickle

from common import *
from TA import *

file = open('keylookup.pickle')
keyLookup = pickle.load(file)
file.close()

def getTeamsFromLog(log,mrayAllowed):
	teams={}
	for team in ['p1team','p2team']:

		teams[team]=[]

		for i in range(len(log[team])):
			if 'species' in log[team][i].keys():
				species = log[team][i]['species']
			else: #apparently randbats usually don't contain the species field?
				species = log[team][i]['name']
			if len(species) == 0:
				sys.stderr.write('Problem with '+filename+'\n')
				return False
			#very odd that these == needed--I've seen ".Species", "(Species)", "species", "Species)", "SPECIES"...
			if species[0] not in string.lowercase + string.uppercase:
				species=species[1:]
			while species[len(species)-1] in ')". ':
				species=species[:len(species)-1]
			species = keyify(species)

			if 'item' in log[team][i].keys():
				item = keyify(log[team][i]['item'])
				if item == '':
					item = 'nothing'
			else:
				item = 'nothing'


			if 'happiness' in log[team][i].keys():
				happiness = log[team][i]['happiness']
			else:
				happiness = 255
			if 'nature' in log[team][i].keys():
				nature = keyify(log[team][i]['nature'])
				if nature not in nmod.keys(): #zarel said this is what PS does
					nature = 'hardy'
			else:
				nature = 'hardy'
			evs = {'hp': 0, 'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0}
			if 'evs' in log[team][i].keys():
				for stat in log[team][i]['evs']:
					evs[stat]=int(log[team][i]['evs'][stat])	
			ivs = {'hp': 31, 'atk': 31, 'def': 31, 'spa': 31, 'spd': 31, 'spe': 31}
			if 'ivs' in log[team][i].keys():
				for stat in log[team][i]['ivs']:
					ivs[stat]=int(log[team][i]['ivs'][stat])
			if 'moves' in log[team][i].keys():
				moves = log[team][i]['moves']
			else:
				moves = []
			while len(moves)<4:
				moves.append('')
			for j in range(len(moves)): #make all moves lower-case and space-free
				old = moves[j]
				try: 
					moves[j] = keyify(moves[j])
				except TypeError:
					moves[j] = ''
			#figure out Hidden Power from IVs
			if 'hiddenpower' in moves:
				hptype=15*(ivs['hp']%2+2*(ivs['atk']%2)+4*(ivs['def']%2)+8*(ivs['spe']%2)+16*(ivs['spa']%2)+32*(ivs['spd']%2))/63
				moves.remove('hiddenpower')
				moves.insert(0,'hiddenpower'+['fighting','flying','poison','ground','rock','bug','ghost','steel','fire','water','grass','electric','psychic','ice','dragon','dark'][hptype])
			if 'ability' in log[team][i].keys():
				ability = keyify(log[team][i]['ability'])
			else:
				ability = 'unknown'
			if 'forcedLevel' in log[team][i].keys():
				level = int(log[team][i]['forcedLevel'])
			elif 'level' in log[team][i].keys():
				level = int(log[team][i]['level'])
			else:
				level = 100

			if species == 'rayquaza' and 'dragonascent' in moves and mrayAllowed:
				species='rayquazamega'
				ability='deltastream'
			elif species == 'greninja' and ability == 'battlebond':
				species = 'greninjaash'
			else: 
				for mega in megas:
					if [species,item] == mega[:2]:
						species = species+'mega'
						if item.endswith('x'):
							species +='x'
						elif item.endswith('y'):
							species += 'y'
						if species in ['kyogremega','groudonmega']:
							species=species[:-4]+'primal'
						ability=mega[2]
						break

			if species[0] in string.lowercase or species[1] in string.uppercase:
				species = species.title()

			for s in aliases: #combine appearance-only variations and weird PS quirks
				if species in aliases[s]:
					species = s
					break
			try:	
				species=keyLookup[keyify(species)]
			except:
				sys.stderr.write(species+' not in keyLookup.\n')
				return False

			for s in aliases: #this 2nd one is needed to deal with Nidoran
				if species in aliases[s]:
					species = s
					break
			
			teams[team].append({
				'species': species,
				'nature': nature,
				'item': item,
				'evs': {},
				'happiness': happiness,
				'moves': [],
				'ability': ability,
				'level': level,
				'ivs': {}})
			for stat in evs:
				teams[team][len(teams[team])-1]['evs'][stat] = evs[stat]
				teams[team][len(teams[team])-1]['ivs'][stat] = ivs[stat]
			for move in moves:
				teams[team][len(teams[team])-1]['moves'].append(move)
	return teams

def LogReader(filename,tier,movesets,ratings):

	mrayAllowed = tier not in ['ubers','battlefactory','megamons', 'gen6ubers', 'gen7ubers', 'gen7pokebankubers']

	file = open(filename)
	raw = file.readline()
	file.close()
	
	if raw=='"log"': #https://github.com/Zarel/Pokemon-Showdown/commit/92a4f85e0abe9d3a9febb0e6417a7710cabdc303
		return False
	try:
		log = json.loads(raw)
	except ValueError:
		sys.stderr.write(filename+' is not a valid log.\n')
		return False

	#determine log type
	spacelog = True
	doublelog = True
	if 'log' in log.keys():
		if log['log'][0][0:2] != '| ':
			spacelog = False

	#check for log length
	#if tier not in ['challengecup1vs1','doublesvgc2013dev','smogondoubles','1v1','gbusingles','globalshowdown']:
	#	longEnough = False
	#	if 'log' not in log.keys():
	#		if int(log['turns']) > 5: 
	#			longEnough = True
	#	else:
	#		for line in log['log']:
	#			if (spacelog and line[2:10] == 'turn | 6') or (not spacelog and line[1:7] == 'turn|6'):
	#				longEnough = True
	#				break
	#	if not longEnough:
	#		return False

	if 'turns' not in log.keys():
		print filename+' has no turn count'
		return False
		

	#get info on the trainers & pokes involved
	ts = []
	rating = {}

	whowon = 0 #0 for tie/unknown, 1 for p1, 2 for p2
	if 'log' in log.keys():
		#if '|tie' in log['log']:
		#	whowon = 0
		if '|win|'+log['p1'] in log['log']:
			whowon = 1
		if '|win|'+log['p2'] in log['log']:
			if whowon == 1:
				sys.stderr.write(filename+'\n')
				sys.stderr.write('This battle had two winners.\n')
				return False
			else:
				whowon = 2
	if ratings == None:
		for i in [['p1rating','p1team'],['p2rating','p2team']]:
			if i[0] in log.keys():
				rating[i[1]]={}
				if type(log[i[0]]) is dict:
					for j in ['r','rd','rpr','rprd']:
						if j in log[i[0]].keys():
							try:
								rating[i[1]][j]=float(log[i[0]][j])
							#looks like it's possible that rating will be recorded as "None". In that case, just
							#treat it as if it's not even there (read: no need to freak out and do the below)

							except TypeError:
								pass
							#	sys.stderr.write('Problem in '+filename+':\n')
							#	sys.stderr.write(i[0]+'['+j+']='+str(log[i[0]][j])+'\n')
							#	return False
								
							
				#gxe = round(10000 / (1 + pow(10.0,(((1500 - rpr)) * math.pi / math.sqrt(3 * pow(math.log(10.0),2.0) * pow(rprd,2.0) + 2500 * (64 * pow(math.pi,2.0) + 147 * pow(math.log(10.0),2))))))) / 100
				#acre= rpr-1.4079126393*rprd
				#not used: 'w','l','t','sigma','rptime','rpsigma','lacre','oldacre','oldrdacre'	
	else:
		for player in [log['p1'],log['p2']]:
			if player not in ratings.keys():
				ratings[player]=Glicko.newPlayer()
		Glicko.update(ratings[log['p1']],ratings[log['p2']],whowon)
		for player in [[log['p1'],'p1team'],[log['p2'],'p2team']]:
			r=ratings[player[0]]['R']
			rd=ratings[player[0]]['RD']
			rpr=Glicko.provisional(ratings[player[0]])['R']
			rprd=Glicko.provisional(ratings[player[0]])['RD']
			rating[player[1]]={'r':r,'rd':rd,'rpr':rpr,'rprd':rprd}

	#get pokemon info
	teams = getTeamsFromLog(log,mrayAllowed)
	if teams == False:
		 sys.stderr.write('Skipping log:\n'+filename+'\n')
		 return False
	for team in ['p1team','p2team']:
		trainer = log[team[:2]]
		for poke in teams[team]:
			ts.append([trainer,poke['species']])
		
		if len(log[team]) < 6:
			for i in range(6-len(log[team])):
				ts.append([trainer,'empty'])
		analysis = analyzeTeam(teams[team])
		
		if analysis is None:
			sys.stderr.write('Problem with '+filename+'\n')
			return False
		teams[team].append({'bias': analysis['bias'], 'stalliness': analysis['stalliness'], 'tags': analysis['tags']})

		for poke in teams[team][:-1]:
			#write to moveset file
			#outname = "Raw/moveset/"+tier+"/"+keyify(species)#+".txt"
			#d = os.path.dirname(outname)
			#if not os.path.exists(d):
			#	os.makedirs(d)
			#msfile=open(outname,'ab')
			if keyify(poke['species']) == 'meloettapirouette':
				print filename
			writeme={'trainer':trainer.encode('ascii', 'ignore'),
				'level':poke['level'],
				'ability':poke['ability'],
				'item':poke['item'],
				'nature':poke['nature'],
				'ivs':poke['ivs'],
				'evs':poke['evs'],
				'moves':poke['moves'],
				'happiness':poke['happiness'],
				'tags':analysis['tags']}
			if team in rating.keys():
				writeme['rating']=rating[team]
			#if whowon == 0:
			#	writeme['outcome']='tie'
			if (team == 'p1team' and whowon == 1) or (team == 'p2team' and whowon == 2):
				writeme['outcome']='win'
			elif whowon != 0:
				writeme['outcome']='loss'
			#msfile.write(lzma.compress(json.dumps(writeme))+'\n')
			#msfile.close()
			if keyify(poke['species']) not in movesets.keys():
				movesets[keyify(poke['species'])]=[]
			movesets[keyify(poke['species'])].append(writeme)


		if (team == 'p1team' and whowon == 1) or (team == 'p2team' and whowon == 2):
			teams[team][len(teams[team])-1]['outcome']='win'
		elif whowon != 0:
			teams[team][len(teams[team])-1]['outcome']='loss'
		if team in rating.keys():
			teams[team][len(teams[team])-1]['rating']=rating[team]

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

	if ts[0][0] == ts[11][0]: #trainer battling him/herself? WTF?
		sys.stderr.write(filename+' had a trainer battling him/herself.\n')
		return False


	#metrics get declared here
	turnsOut = [] #turns out on the field (a measure of stall)
	KOs = [] #number of KOs in the battle
	matchups = [] #poke1, poke2, what happened

	for i in range(0,12):
		turnsOut.append(0)
		KOs.append(0)

	if 'log' in log.keys() and tier not in nonSinglesFormats:
		#determine initial pokemon
		active = [-1,-1]
		for line in log['log']:
			if len(line) < 2 or not line.startswith('|'):
				continue
			parsed_line = [segment.strip() for segment in line.split('|')]
			if len(parsed_line) < 2:
				sys.stderr.write('Problem with '+filename+'\n')
				sys.stderr.write('Could not parse line:\n')
				sys.stderr.write(line + '\n')
				return False

			if parsed_line[1] == 'switch' and parsed_line[2].startswith('p1'):
				if len(parsed_line) < 4:
					sys.stderr.write('Problem with '+filename+'\n')
					sys.stderr.write('Could not parse line:\n')
					sys.stderr.write(line + '\n')
					return False

				species = parsed_line[3]
				# remove gender
				species = species.split(',')[0]

				for s in aliases: #combine appearance-only variations and weird PS quirks
					if species in aliases[s]:
						species = s
						break

				try:
					active[0]=ts.index([ts[0][0],species])
				except ValueError:
					#try undoing a mega evolution
					if species == 'Greninja-Ash':
						speciesBase = 'Greninja'
					elif species == 'Zygarde-Complete':
						speciesBase = 'Zygarde'
					elif species.startswith('Mimikyu'):
						speciesBase = 'Mimikyu'
					elif species == 'Necrozma-Ultra':
						speciesBase = 'Necrozma'
					elif species.endswith('-Mega') or species.endswith('-Mega-X') or species.endswith('-Mega-Y') or species.endswith('-Primal'):
						if species.endswith('-Mega'):
							speciesBase = species[:-5]
						else:
							speciesBase = species[:-7]
					else:
						speciesBase = species

					for i in xrange(6):
						if ts[i][1].startswith(speciesBase):
							species = ts[i][1]
							active[0] = i
					if active[0]==-1:
						sys.stderr.write('Problem with '+filename+'\n')
						sys.stderr.write('(Pokemon not in ts) (1)\n')
						sys.stderr.write(str([ts[0][0],species])+'\n')
						return False
			
			if parsed_line[1] == 'switch' and parsed_line[2].startswith('p2'):
				if len(parsed_line) < 4:
					sys.stderr.write('Problem with '+filename+'\n')
					sys.stderr.write('Could not parse line:\n')
					sys.stderr.write(line + '\n')
					return False

				species = parsed_line[3]
				# remove gender
				species = species.split(',')[0]

				for s in aliases: #combine appearance-only variations and weird PS quirks
					if species in aliases[s]:
						species = s
						break	

				try:
					active[1]=ts.index([ts[11][0],species])
				except ValueError:
					#try undoing a mega evolution
					if species == 'Greninja-Ash':
						speciesBase = 'Greninja'
					elif species == 'Zygarde-Complete':
						speciesBase = 'Zygarde'
					elif species.startswith('Mimikyu'):
						speciesBase = 'Mimikyu'
					elif species == 'Necrozma-Ultra':
						speciesBase = 'Necrozma'
					elif species.endswith('-Mega') or species.endswith('-Mega-X') or species.endswith('-Mega-Y') or species.endswith('-Primal'):
						if species.endswith('-Mega'):
							speciesBase = species[:-5]
						else:
							speciesBase = species[:-7]
					else:
						speciesBase = species

					for i in xrange(6,12):
						if ts[i][1].startswith(speciesBase):
							species = ts[i][1]
							active[1] = i
					if active[1]==-1:
						sys.stderr.write('Problem with '+filename+'\n')
						sys.stderr.write('(Pokemon not in ts) (2)\n')
						sys.stderr.write(str([ts[11][0],species])+'\n')
						return False
				break
		start=log['log'].index(line)+1

		for i in range(0,12):
			turnsOut.append(0)
			KOs.append(0)

		#parse the damn log

		#flags
		roar = False
		uturn = False
		fodder = False
		hazard = False
		ko = [False,False]
		switch = [False,False]
		uturnko = False
		mtemp = []

		for line in log['log'][start:]:
			if len(line) < 2 or not line.startswith('|'):
				continue
			parsed_line = [segment.strip() for segment in line.split('|')]
			#print line
			#identify what kind of message is on this line
			if len(parsed_line) < 2:
				sys.stderr.write('Problem with '+filename+'\n')
				sys.stderr.write('Could not parse line:\n')
				sys.stderr.write(line)
				return False
			linetype = parsed_line[1]

			if linetype == "turn":
				matchups = matchups + mtemp
				mtemp = []

				#reset for start of turn
				roar = uturn = uturnko = fodder = hazard = False
				ko = [False,False]
				switch = [False,False]

				#Mark each poke as having been out for an additional turn
				turnsOut[active[0]]=turnsOut[active[0]]+1
				turnsOut[active[1]]=turnsOut[active[1]]+1

			elif linetype in ["win","tie"]: 
				#close out last matchup
				if ko[0] or ko[1]: #if neither poke was KOed, match ended in forfeit, and we don't care
					matchup = [ts[active[0]][1],ts[active[1]][1],12]
					if ko[0] and ko[1]:
						KOs[active[0]] = KOs[active[0]]+1
						KOs[active[1]] = KOs[active[1]]+1
						matchup[2]=2#double down
					else:
						KOs[active[ko[0]]] = KOs[active[ko[0]]]+1
						matchup[2] = ko[1]	#0: poke1 was KOed
									#1: poke2 was KOed
						if uturnko: #would rather not use this flag...
							mtemp=mtemp[:len(mtemp)-1]
							matchup[2] = matchup[2] + 8	#8: poke1 was u-turn KOed
											#9: poke2 was u-turn KOed
						
					mtemp.append(matchup)
				matchups=matchups+mtemp
			

			elif linetype == "move": #check for Roar, etc.; U-Turn, etc.
				hazard = False
				#identify attacker and skip its name
				found = False
				if doublelog:
					line=line[:8+3*spacelog]+line[9+3*spacelog:]
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
						if line[6+3*spacelog:].startswith(tempnicks[i]):
							if found:
								if len(tempnicks[i]) < len(found):
									continue
							found = tempnicks[i]
							foundidx = i
					if found:
						nicks[i]=found
					else:
						tryAgain = False
						for i in range(len(tempnicks)):
							if len(tempnicks[i])>1:
								tryAgain = True
								break
						if not tryAgain:
							sys.stderr.write("Nick not found.\n")
							sys.stderr.write("In file: "+argv[1]+"\n")
							sys.stderr.write(line[6+3*spacelog:]+"\n")
							sys.stderr.write(str(nicks)+"\n")
							return False
						
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
				p=int(line[8+3*spacelog])-1
				ko[p]=1
				if switch[p]==1: #fainted on the same turn that it was switched in
					fodder=True
			
				if uturn:
					uturn=False
					uturnko=True

			elif linetype == "replace": #it was Zorua/Zoroark all along!
				p=10+3*spacelog

				if len(parsed_line) < 4:
					sys.stderr.write('Problem with '+filename+'\n')
					sys.stderr.write('Could not parse line:\n')
					sys.stderr.write(line)
					return False

				species = parsed_line[3]
				# remove gender
				species = species.split(',')[0]

				for s in aliases: #combine appearance-only variations and weird PS quirks
					if species in aliases[s]:
						species = s
						break

				if [ts[11*(int(line[p])-1)][0],species] not in ts:
					if species == 'Shaymin' and [ts[11*(int(line[p])-1)][0],'Shaymin-Sky'] in ts:
						#if Shaymin-Sky gets frozen, it reverts to land forme
						species = 'Shaymin-Sky'
					else:
						found = False
						#try undoing a mega evolution
						if species == 'Greninja-Ash':
							speciesBase = 'Greninja'
						elif species == 'Zygarde-Complete':
							speciesBase = 'Zygarde'
						elif species.startswith('Mimikyu'):
							speciesBase = 'Mimikyu'
						elif species == 'Necrozma-Ultra':
							speciesBase = 'Necrozma'
						elif species.endswith('-Mega') or species.endswith('-Mega-X') or species.endswith('-Mega-Y') or species.endswith('-Primal'):
							if species.endswith('-Mega'):
								speciesBase = species[:-5]
							else:
								speciesBase = species[:-7]
						else:
							speciesBase = species

						for i in xrange(6*(int(line[p])-1),6*int(line[p])):
							if ts[i][1].startswith(speciesBase):
								species = ts[i][1]
								found = True
								break
						if not found:
							#maybe it's a nickname thing
							nick = species[species.find(' ')+1:]
							player_no = int(species[1])
							for i in range(6):
								if nicks[2*i+player_no-1].endswith(nick):
									found = True
									species = ts[6*(player_no-1)+i][1]
									break
						if not found:
							sys.stderr.write('Problem with '+filename+'\n')
							sys.stderr.write('(Pokemon not in ts) (3)\n')
							sys.stderr.write(str([ts[11*(int(line[p])-1)][0],species])+'\n')
							return False
				active[int(line[p])-1]=ts.index([ts[11*(int(line[p])-1)][0],species])
				#really, it would be better to go back and revise previous affected matchups, but that be a lot more work

			elif linetype in ["switch","drag"]: #switch out: new matchup!
				if linetype == "switch":
					p=9+3*spacelog
				else:
					p=7+3*spacelog	
				switch[int(line[p])-1]=True

				if switch[0] and switch[1] and not fodder: #need to revise previous matchup
					matchup=mtemp[len(mtemp)-1]
					matchup[2]=12
					if (not ko[0]) and (not ko[1]): #double switch
						matchup[2]=5 
					elif ko[0] and ko[1]: #double down
						KOs[active[ko[0]]] = KOs[active[ko[0]]]+1
						matchup[2]=2
					else: #u-turn KO (note that this includes hit-by-red-card-and-dies and roar-then-die-by-residual-dmg)
						KOs[active[ko[0]]] = KOs[active[ko[0]]]+1
						matchup[2]=ko[1]+8
					mtemp[len(mtemp)-1]=matchup
				else:
					#close out old matchup
					#it is utterly imperative that the p1 poke goes first and the p2 poke second
					matchup = [ts[active[0]][1],ts[active[1]][1],12]
					#if ko[0] and ko[1]: #double down
					if ko[0] or ko[1]:
						if fodder and hazard: #if dies on switch-in due to an attack, it's still "KOed"
							matchup[2] = ko[1]+10 #foddered
						else:
							KOs[active[ko[0]]] = KOs[active[ko[0]]]+1
							matchup[2] = ko[1]
					else:
						matchup[2]=3+switch[1]  #3: poke1 switched out
									#4: poke2 switched out
						if roar:
							matchup[2]=matchup[2]+3	#6: poke1 was forced out
										#7: poke2 was forced out
					mtemp.append(matchup)
		
				#new matchup!
				uturn = roar = fodder = False
				hazard = True

				if len(parsed_line) < 4:
					sys.stderr.write('Problem with '+filename+'\n')
					sys.stderr.write('Could not parse line:\n')
					sys.stderr.write(line)
					return False

				species = parsed_line[3]
				# remove gender
				species = species.split(',')[0]
				while ',' in species:
					species = species[0:string.rfind(species,',')]
				for s in aliases: #combine appearance-only variations and weird PS quirks
					if species in aliases[s]:
						species = s
						break

				if [ts[11*(int(line[p])-1)][0],species] not in ts:
					if species == 'Shaymin' and [ts[11*(int(line[p])-1)][0],'Shaymin-Sky'] in ts:
					#if Shaymin-Sky gets frozen, it reverts to land forme
						species = 'Shaymin-Sky'
					else:
						found = False
						#try undoing a mega evolution
						if species == 'Greninja-Ash':
							speciesBase = 'Greninja'
						elif species == 'Zygarde-Complete':
							speciesBase = 'Zygarde'
						elif species.startswith('Mimikyu'):
							speciesBase = 'Mimikyu'
						elif species == 'Necrozma-Ultra':
							speciesBase = 'Necrozma'
						elif species.endswith('-Mega') or species.endswith('-Mega-X') or species.endswith('-Mega-Y') or species.endswith('-Primal'):
							if species.endswith('-Mega'):
								speciesBase = species[:-5]
							else:
								speciesBase = species[:-7]
						else:
							speciesBase = species

						for i in xrange(6*(int(line[p])-1),6*int(line[p])):
							if ts[i][1].startswith(speciesBase):
								species = ts[i][1]
								found = True
								break
						if not found:
							print ts
							sys.stderr.write('Problem with '+filename+'\n')
							sys.stderr.write('(Pokemon not in ts) (4)\n')
							sys.stderr.write(str([ts[11*(int(line[p])-1)][0],species])+'\n')
							return False
				active[int(line[p])-1]=ts.index([ts[11*(int(line[p])-1)][0],species])

	for i in range(len(matchups)):
		if matchups[i][2] == False:
			matchups[i][2] = 0 #serves me right for playing it fast & loose with T/F vs. 1/0

	#totalTurns = log['turns']
	#totalKOs = sum(KOs)

	writeme = {}
	
	writeme['p1'] = {'trainer':ts[0][0].encode('ascii','replace')}
	
	teamtags = teams['p1team'][len(teams['p1team'])-1]
	for x in teamtags.keys():
		writeme['p1'][x] = teamtags[x]
	writeme['p1']['team']=[]
	i=0
	while (ts[i][0] == ts[0][0]):
		writeme['p1']['team'].append({'species':ts[i][1],'KOs':KOs[i],'turnsOut':turnsOut[i]})
		i = i+1
		if i>=len(ts):
			sys.stderr.write("Something's wrong here.\n")
			sys.stderr.write("In file: "+argv[1]+"\n")
			sys.stderr.write(str(ts)+"\n")
			return False

	writeme['p2'] = {'trainer':ts[len(ts)-1][0].encode('ascii','replace')}
	teamtags = teams['p2team'][len(teams['p2team'])-1]
	for x in teamtags.keys():
		writeme['p2'][x] = teamtags[x]
	writeme['p2']['team']=[]
	for j in range(i,len(ts)):
		writeme['p2']['team'].append({'species':ts[j][1],'KOs':KOs[j],'turnsOut':turnsOut[j]})
	writeme['matchups']=matchups
	writeme['turns']=int(log['turns'])
	if 'endType' in log.keys():
		writeme['endType']=log['endType']
	
	#outfile.write(lzma.compress(json.dumps(writeme))+'\n')
	return writeme

def main(argv):
	tier = argv[2]
	if tier.endswith('current'):
		tier=tier[:-7]
	if tier.startswith('pokebank'):
		tier = tier[8:-4]
	if tier.startswith('oras'):
		tier = tier[4:]
	if tier == 'capbeta':
		tier = 'cap'
	if tier == 'vgc2014beta':
		tier = 'vgc2014'
	if tier.startswith('xybattlespot') and tier.endswith('beta'):
		tier = tier[:-4]
	if tier in ['battlespotdoubles', 'battlespotdoublesvgc2015']:
		tier = 'vgc2015'
	if tier == 'smogondoubles':
		tier = 'doublesou'
	if tier == 'smogondoublesubers':
		tier = 'doublesubers'
	if tier == 'smogondoublesuu':
		tier = 'doublesuu'
	#elif tier[:8]=='seasonal':
	#	tier='seasonal'

	ratings = None
	if len(argv) > 4:
		if argv[3] == '-redoRatings':
			try:
				ratings = json.loads(open(argv[4]).readline())
			except:
				ratings = {}
			print ratings

	outname = "Raw/"+tier#+".txt"
	d = os.path.dirname(outname)
	if not os.path.exists(d):
		os.makedirs(d)
	writeme=[]
	movesets={}
	count=0
	for filename in os.listdir(argv[1]):
		#print filename
		x = LogReader(argv[1]+'/'+filename,tier,movesets,ratings)
		if x:
			writeme.append(x)
			count += 1
			
			if count % 10000 == 0:
				outname = "Raw/"+tier#+".txt"
				outfile=gzip.open(outname,'ab')
				outfile.write(json.dumps(writeme)+'\n')
				outfile.close()

				#write to moveset file
				for species in movesets.keys():
					outname = "Raw/moveset/"+tier+"/"+species#+".txt"
					d = os.path.dirname(outname)
					if not os.path.exists(d):
						os.makedirs(d)
					msfile=gzip.open(outname,'ab')		
					msfile.write(json.dumps(movesets[species]))
					msfile.close()

				writeme = []
				movesets={}
	if writeme:
		outname = "Raw/"+tier#+".txt"
		outfile=gzip.open(outname,'ab')
		outfile.write(json.dumps(writeme)+'\n')
		outfile.close()

		#write to moveset file
		for species in movesets.keys():
			outname = "Raw/moveset/"+tier+"/"+species#+".txt"
			d = os.path.dirname(outname)
			if not os.path.exists(d):
				os.makedirs(d)
			msfile=gzip.open(outname,'ab')		
			msfile.write(json.dumps(movesets[species]))
			msfile.close()

	if ratings != None:
		for player in ratings.keys():
			Glicko.newRatingPeriod(ratings[player])
		ratingfile=open(argv[4],'w+')
		ratingfile.write(json.dumps(ratings))
		ratingfile.close()

if __name__ == "__main__":
    main(sys.argv)
