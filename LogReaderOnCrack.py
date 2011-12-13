#!/usr/bin/python
import string
import sys
filename = str(sys.argv[1])
file = open(filename)
log = file.readlines()

oldWay = False
if len(sys.argv) > 2:
	if sys.argv[2] == '-old':
		oldWay = True

if (len(log) < 15):
	sys.exit()

doubles = False
#determine tier
if log[2][0:25] == '<div class="TierSection">':
	tier = log[2][string.find(log[2],"</b>")+4:len(log[2])-7]
	if log[3][0:19] == '<div class="Rated">':
		rated = log[3][string.find(log[3],"</b>")+4:len(log[3])-7]
	else:
		if log[5][0:19] == '<div class="Rated">':
			rated = log[5][string.find(log[5],"</b>")+4:len(log[5])-7]
		else:
			print "Can't find the rating for "+filename
			for line in range(0,15):
				print log[line]
			sys.exit()
else:
	if log[5][0:25] != '<div class="TierSection">':
		print "Can't find the tier for "+filename
		sys.exit()
	tier = log[5][string.find(log[5],"</b>")+4:len(log[5])-7]
	if log[6][0:19] == '<div class="Rated">':
		rated = log[6][string.find(log[6],"</b>")+4:len(log[6])-7]
	else:
		if log[8][0:19] == '<div class="Rated">':
			rated = log[8][string.find(log[8],"</b>")+4:len(log[8])-7]
		else:
			print "Can't find the rating for "+filename
			for line in range(0,15):
				print log[line]
			sys.exit()

#if tier != 'Standard OU' or rated != 'Rated':
#	sys.exit()
if tier in ['VGC 2009', 'VGC 2010', 'VGC 2011', 'VGC 2012']:
	doubles = True
#make sure the battle lasted at least six turns (to discard early forfeits)
longEnough = False
for line in log:
	if line == '<div class="BeginTurn"><b><span style=\'color:#0000ff\'>Start of turn 6</span></b></div>\n':
		longEnough = True
		break
if (longEnough == False) and (doubles == false):
	sys.exit()

#get info on the trainers & pokes involved
ts = []
skip = 0
if oldWay == False:
	for line in range(1,len(log)):
		if log[line][0:19] == '<div class="Teams">':
			for x in range(0,2):
				trainer = log[line+x][50:string.rfind(log[line+x],"'s team:")]
				if string.find(trainer,"send out") > -1:
					print trainer+" is a dick."
					sys.exit()
				stemp = ""
				for i in range(string.rfind(log[line+x],"</span></b>")+11,len(log[line+x])):
					if log[line+x][i:i+3] == ' / ':
						ts.append([trainer,stemp])
						stemp=""
						skip = 3
					if log[line+x][i] == '<':
						break
					if skip > 0:
						skip=skip-1
					else:
						stemp = stemp+log[line+x][i]
				ts.append([trainer,stemp])
			break

if (line == len(log)) or oldWay == True: #it's an old log, so find pokes the old way
	#find all "sent out" messages
	for line in range(5,len(log)):
		if log[line][0:21] == '<div class="SendOut">':
			ttemp = log[line][21:string.find(log[line],' sent out ')]
			#determine whether the pokemon is nicknamed or not
			if log[line][len(log[line])-8] == ')':
				stemp = log[line][string.rfind(log[line],'(')+1:len(log[line])-8]
			else:
				stemp = log[line][string.rfind(log[line],'sent out ')+9:len(log[line])-8]

			#determine whether this entry is already in the list
			match = 0
			for i in range(0,len(ts)):
				if (ts[i][0] == ttemp) & (ts[i][1] == stemp):
					match = 1
					break
			if match == 0:
				ts.append([ttemp,stemp])
	ts=sorted(ts, key=lambda ts:ts[0])
	#gotta fill in the gaps
	i=0
	while (ts[i][0] == ts[0][0]):
		i=i+1
	if i<6:
		for j in range(i,6):
			ts.append([ts[0][0],"???"])
	ts=sorted(ts, key=lambda ts:ts[0])
	if len(ts)<12:
		i=len(ts)
		for j in range(i,12):
			ts.append([ts[6][0],"???"])

#find where battle starts
active = [-1,-1]
t=0
for line in range(1,len(log)):
	if log[line][0:21] == '<div class="SendOut">':
		for x in range(0,2):
			#ID trainer
			trainer = log[line+x][21:string.find(log[line+x],' sent out ')]
			if trainer == ts[0][0]:
				t=0
			else:
				t=1
			#it matters whether the poke is nicknamed or not
			if log[line+x][len(log[line+x])-8] == ')':
				species = log[line+x][string.rfind(log[line+x],'(')+1:len(log[line+x])-8]
			else:
				species = log[line+x][string.rfind(log[line+x],'sent out ')+9:len(log[line+x])-8]
			for i in range(0,6):
				if species == ts[6*t+i][1]:
					active[t] = i
					break
		break
start = line +2

#metrics get declared here
turnsOut = [] #turns out on the field (a measure of stall)
KOs = [] #number of KOs in the battle
matchups = [] #poke1, poke2, what happened

for i in range(0,12):
	turnsOut.append(0)
	KOs.append(0)

#parse the damn log
if doubles == True:
	for i in range(0,12):
		turnsOut[i] = 1
		KOs[i] = 0
else:
	#flags
	roar = 0
	uturn = 0
	ko = 0
	switch = 0
	doubleSwitch = -1
	uturnko = 0
	ignore = 0

	for line in range(start,len(log)):
		#identify what kind of message is on this line
		linetype = log[line][12:string.find(log[line],'">')]

		if linetype == "BeginTurn":
			#reset for start of turn
			roar = uturn = switch = ko = uturnko = 0
			doubleSwitch = -1

			#Mark each poke as having been out for an additional turn
			turnsOut[active[0]]=turnsOut[active[0]]+1
			turnsOut[active[1]+6]=turnsOut[active[1]+6]+1

		if linetype == "UseAttack": #check for Roar, etc.; U-Turn, etc.
			#identify move
			move = log[line][string.rfind(log[line],"'>")+2:len(log[line])-19]
			if move in ["Roar","Whirlwind","Circle Throw","Dragon Tail"]:
				roar = 1
			elif move in ["U-Turn","Volt Switch","Baton Pass"]:
				if line+3 < len(log):
					if log[line][12:string.find(log[line],'">')] == "SendBack":
						uturn = 1

		elif linetype == "ItemMessage": #check for Red Card, Eject Button
			#search for relevant items
			if string.rfind(log[line],"Red Card") > -1:
				roar = 1
			elif string.rfind(log[line],"Eject Button") > -1:
				uturn = 1

		elif linetype == "Ko": #KO
			ko = ko+1
		
			#make sure it's not the end of the battle
			o = p = 0
			if line+2 < len(log):
				o = 1
			if line+1 < len(log):
				p = 1
			if log[line+2*o][12:string.find(log[line+2*o],'">')] == "BattleEnd":
				pokes = [ts[active[0]][1],ts[active[1]+6][1]]
				matchup=pokes[0]+' vs. '+pokes[1]+': '
				if ko == 1:
					KOs[active[(t+1)%2]+6*((t+1)%2)]=KOs[active[(t+1)%2]+6*((t+1)%2)]+1
					matchup = matchup + ts[active[t]+6*t][1] + " was KOed"
				elif ko == 2:
					KOs[active[0]] = KOs[active[0]]+1
					KOs[active[1]+6] = KOs[active[1]+6]+1
					matchup = matchup + "double down"
				else:
					matchup = matchup + "no clue what happened"
				matchups.append(matchup)
			elif log[line+p][12:string.find(log[line+p],'">')] == "SendBack":
				uturnko=1
		elif linetype == "SendBack": #switch out
			switch = 1
		elif linetype == "SendOut":
			#ID trainer
			trainer = log[line][21:string.find(log[line],' sent out ')]
			if trainer == ts[0][0]:
				t=0
			else:
				t=1
		
			#make sure it's not a double-switch
			o = 0
			if line+2 < len(log):
				o = 1
			if ignore == 1:
				ignore = 0
			elif (o == 1) and (log[line+2*o][12:string.find(log[line+2*o],'">')] == "SendBack"):
				doubleSwitch = active[t]+t*6
			else:
				#close out old matchup
				if doubleSwitch > -1:
					pokes = [ts[active[0]][1],ts[doubleSwitch][1]]
				else:
					pokes = [ts[active[0]][1],ts[active[1]+6][1]]
			
				pokes=sorted(pokes, key=lambda pokes:pokes)
				matchup=pokes[0]+' vs. '+pokes[1]+': '
				if doubleSwitch > -1:
					matchup = matchup + "double switch"
				elif (uturnko == 1):
					KOs[active[(t+1)%2]+6*((t+1)%2)]=KOs[active[(t+1)%2]+6*((t+1)%2)]+1
					matchup = matchup + ts[active[(t+1)%2]+((t+1)%2)*6][1] + " was u-turn KOed"
					ignore = 1
				elif ko == 1:
					KOs[active[(t+1)%2]+6*((t+1)%2)]=KOs[active[(t+1)%2]+6*((t+1)%2)]+1
					matchup = matchup + ts[active[t]+6*t][1] + " was KOed"
				elif ko == 2:
					KOs[active[0]] = KOs[active[0]]+1
					KOs[active[1]+6] = KOs[active[1]+6]+1
					matchup = matchup + "double down"
					ignore = 1
				elif roar == 1:
					matchup = matchup + ts[active[t]+6*t][1] + " was forced out"
				elif (uturn == 1) or (switch == 1):
					matchup = matchup + ts[active[t]+6*t][1] + " was switched out"
				else:
					matchup = matchup + "no clue what happened"
				matchups.append(matchup)

			#new matchup!
			uturn = roar = 0
			#it matters whether the poke is nicknamed or not
			if log[line][len(log[line])-8] == ')':
				species = log[line][string.rfind(log[line],'(')+1:len(log[line])-8]
			else:
				species = log[line][string.rfind(log[line],'sent out ')+9:len(log[line])-8]
			for i in range(0,6):
				if species == ts[6*t+i][1]:
					active[t] = i
					break
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
	
