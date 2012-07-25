#!/usr/bin/python
import string
import sys
import json
filename = str(sys.argv[1])
file = open(filename)
raw = file.readline()
file.close()
log = json.loads(raw)

#check for log length
longEnough = False
for line in log['log']:
	if line[2:10] == 'turn | 6':
		longEnough = True
		break
if not longEnough:
	sys.exit(0)

#get info on the trainers & pokes involved
ts = []
trainer = log['p1']
for i in range(0,6):
	ts.append([trainer,log['p1team'][i]['species']])
trainer = log['p2']
for i in range(0,6):
	ts.append([trainer,log['p2team'][i]['species']])

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
	'Rotom- C' : 'Rotom-Mow'
}

for i in replacements:
	for j in range(len(ts)):
		if ts[j][1] == i:
			ts[j][1] = replacements[i]

#nickanmes
nicks = []
for i in range(0,6):
	nicks.append("p1: "+log['p1team'][i]['name'])
	nicks.append("p2: "+log['p2team'][i]['name'])

#determine initial pokemon
active = [-1,-1]
for line in log['log']:
	if line[0:14] == "| switch | p1:":
		end = string.rfind(line,'|')-1
		species = line[string.rfind(line,'|',15,end-1)+2:end]
		while ',' in species:
			species = species[0:string.rfind(species,',')]
		active[0]=ts.index([ts[0][0],species])
	if line[0:14] == "| switch | p2:":
		end = string.rfind(line,'|')-1
		species = line[string.rfind(line,'|',15,end-1)+2:end]
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
	linetype = line[2:string.find(line,'|',2)-1]

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
			if line[9:].startswith(nick):
				found = True
				break
		if not found:
			print "Uh oh!"
			print line[9:]
			sys.exit(1)
		
		move = line[9+len(nick)+3:string.find(line,"|",9+len(nick)+3)-1]
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
		ko[int(line[11])-1]=1

		if uturn:
			uturn=False
			uturnko=True

	elif linetype in ["switch","drag"]: #switch out: new matchup!
		if linetype == "switch":
			p=12
		else:
			p=10	
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
		end = string.rfind(line,'|')-1
		species = line[string.rfind(line,'|',15,end-1)+2:end]
		while ',' in species:
			species = species[0:string.rfind(species,',')]
		active[int(line[p])-1]=ts.index([ts[11*(int(line[p])-1)][0],species])

tier = sys.argv[2]
rated = "Rated"

outname = "Raw/"+tier+" "+rated+".txt"
outfile=open(outname,'a')

outfile.write(str(ts[0][0]))
outfile.write("\n")
i=0
while (ts[i][0] == ts[0][0]):
	outfile.write(ts[i][1]+" ("+str(KOs[i])+","+str(turnsOut[i])+")\n")
	i = i + 1
outfile.write("***\n")
outfile.write(str(ts[len(ts)-1][0]))
outfile.write("\n")
for j in range(i,len(ts)):
	outfile.write(ts[j][1]+" ("+str(KOs[j])+","+str(turnsOut[j])+")\n")
outfile.write("@@@\n")
for line in matchups:
	outfile.write(line+"\n")
outfile.write("---\n")
outfile.close()	

