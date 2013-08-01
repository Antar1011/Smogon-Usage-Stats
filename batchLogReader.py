#!/usr/bin/python
# -*- coding: latin-1 -*-
#File I/O is going to be the main bottleneck. Doing log reading in batch (a folder at a time, rather than log by log)
#should be much more efficient, as TA.py and the files it requires need only be loaded once per run.

import string
import sys
import json
import lzma
import copy
#import cPickle as pickle
import math
import os

from common import *
from TA import *

def LogReader(filename,tier,movesets):
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
	if tier not in ['challengecup1v1','doublesvgc2013dev','smogondoubles','1v1','gbusingles','globalshowdown']:
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
			return False

	#get info on the trainers & pokes involved
	ts = []
	teams = {}
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
			teams[team].append({
				'species': keyify(species),
				'nature': nature,
				'item': item,
				'evs': {},
				'moves': [],
				'ability': ability,
				'level': level,
				'ivs': {}})
			for stat in evs:
				teams[team][len(teams[team])-1]['evs'][stat] = evs[stat]
				teams[team][len(teams[team])-1]['ivs'][stat] = ivs[stat]
			for move in moves:
				teams[team][len(teams[team])-1]['moves'].append(move)

			#write to moveset file
			#outname = "Raw/moveset/"+tier+"/"+keyify(species)#+".txt"
			#d = os.path.dirname(outname)
			#if not os.path.exists(d):
			#	os.makedirs(d)
			#msfile=open(outname,'ab')
			writeme={'trainer':trainer.encode('ascii', 'ignore'),
				'level':level,
				'ability':ability,
				'item':item,
				'nature':nature,
				'ivs':ivs,
				'evs':evs,
				'moves':moves}
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
			if keyify(species) not in movesets.keys():
				movesets[keyify(species)]=[]
			movesets[keyify(species)].append(writeme)

		if len(log[team]) < 6:
			for i in range(6-len(log[team])):
				ts.append([trainer,'empty'])
		analysis = analyzeTeam(teams[team])
		teams[team].append({'bias': analysis['bias'], 'stalliness': analysis['stalliness'], 'tags': analysis['tags']})
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

	if 'log' in log.keys() and tier not in ['doublesvgc2013dev','smogondoubles']: #doubles not currently supported
		#determine initial pokemon
		active = [-1,-1]
		for line in log['log']:
			if (spacelog and line[0:13] == "| switch | p1") or (not spacelog and line[0:10] == "|switch|p1"):
				if line[10+3*spacelog] == ':':
					doublelog = False
				end = string.rfind(line,'|')-1*spacelog
				species = line[string.rfind(line,'|',12+3*spacelog,end-1)+1+1*spacelog:end]
				while ',' in species:
					species = species[0:string.rfind(species,',')]
				for s in aliases: #combine appearance-only variations and weird PS quirks
					if species in aliases[s]:
						species = s
						break
				active[0]=ts.index([ts[0][0],species])
			if (spacelog and line[0:13] == "| switch | p2") or (not spacelog and line[0:10] == "|switch|p2"):
				end = string.rfind(line,'|')-1*spacelog
				species = line[string.rfind(line,'|',12+3*spacelog,end-1)+1+1*spacelog:end]
				while ',' in species:
					species = species[0:string.rfind(species,',')]
				for s in aliases: #combine appearance-only variations and weird PS quirks
					if species in aliases[s]:
						species = s
						break
				active[1]=ts.index([ts[11][0],species])
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
			#print line
			#identify what kind of message is on this line
			linetype = line[1+1*spacelog:string.find(line,'|',1+1*spacelog)-1*spacelog]

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
							sys.stderr.write("In file: "+sys.argv[1]+"\n")
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

				end = string.rfind(line,'|')-1*spacelog
				species = line[string.rfind(line,'|',0,end-1)+1+1*spacelog:end]
				while ',' in species:
					species = species[0:string.rfind(species,',')]
				for s in aliases: #combine appearance-only variations and weird PS quirks
					if species in aliases[s]:
						species = s
						break
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
				#it matters whether the poke is nicknamed or not
				end = string.rfind(line,'|')-1*spacelog
				species = line[string.rfind(line,'|',0,end-1)+1+1*spacelog:end]
				while ',' in species:
					species = species[0:string.rfind(species,',')]
				for s in aliases: #combine appearance-only variations and weird PS quirks
					if species in aliases[s]:
						species = s
						break
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
			sys.stderr.write("In file: "+sys.argv[1]+"\n")
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
	
	#outfile.write(lzma.compress(json.dumps(writeme))+'\n')
	return writeme

tier = sys.argv[2]
if tier[len(tier)-7:]=='current':
	tier=tier[:len(tier)-7]
#elif tier[:8]=='seasonal':
#	tier='seasonal'
outname = "Raw/"+tier#+".txt"
d = os.path.dirname(outname)
if not os.path.exists(d):
	os.makedirs(d)
writeme=[]
movesets={}
for filename in os.listdir(sys.argv[1]):
	#print filename
	x = LogReader(sys.argv[1]+'/'+filename,tier,movesets)
	if x:
		writeme.append(x)
outfile=open(outname,'ab')
outfile.write(lzma.compress(json.dumps(writeme)))
outfile.close()	

#write to moveset file
for species in movesets.keys():
	outname = "Raw/moveset/"+tier+"/"+species#+".txt"
	d = os.path.dirname(outname)
	if not os.path.exists(d):
		os.makedirs(d)
	msfile=open(outname,'ab')		
	msfile.write(lzma.compress(json.dumps(movesets[species])))
	msfile.close()

