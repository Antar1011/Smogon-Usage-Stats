#!/usr/bin/python
import string
import sys

def readTable(filename,col,weight,usage):
	file = open(filename)
	table=file.readlines()
	file.close()

	#'real' usage screwed me over--I can't take total count from header
	#using percentages is a bad idea because of roundoff

	tempUsage = [0 for i in range(len(pokelist))] #really dumb that I have to do this

	for i in range(6,len(table)):
		name = table[i][10:26]
	
		if (name[0] == '-'):
			break

		while name[len(name)-1] == ' ': 
			#remove extraneous spaces
			name = name[0:len(name)-1]
	
		count = table[i][28:35]
		while count[len(count)-1] == ' ':
			#remove extraneous spaces
			count = count[0:len(count)-1]
		found = False
		for j in range(0,len(lsname)):
			if name == lsname[j]:
				tempUsage[j]=float(count)
				found = True
				break
		if not found:
			print name+" not found!"
			sys.exit() 

	for i in range(0,len(tempUsage)):
		usage[i][col] = usage[i][col]+weight*6.0*tempUsage[i]/sum(tempUsage)/24

def makeTable(table,name,newTiers):

	print "[HIDE="+name+"][CODE]"
	print "Three-month usage for Standard "+name
	print " + ---- + --------------- + ------- + "
	print " | Rank | Pokemon         | Percent | "
	print " + ---- + --------------- + ------- + "
	print ' [B]| %-4d | %-15s | %6.3f%% |' % (1,lsname[table[0][0]],table[0][1]*100)
	for i in range(1,len(table)):
		if table[i][1] < 0.0340636711:
			start = i
			break
		print ' | %-4d | %-15s | %6.3f%% |' % (i+1,lsname[table[i][0]],100.0*table[i][1])
	print '[/B] | %-4d | %-15s | %6.3f%% |' % (i+1,lsname[table[i][0]],100.0*table[i][1])
	for i in range(0,start):
		if (newTiers[table[i][0]] == 'PU'):
			newTiers[table[i][0]] = name
	for i in range(start+1,len(table)):
		print ' | %-4d | %-15s | %6.3f%% |' % (i+1,lsname[table[i][0]],100.0*table[i][1])
	print " + ---- + --------------- + ------- +[/CODE][/HIDE]"

file = open("pokemons.txt")
pokelist = file.readlines()
file.close()

file = open("NU.txt")
NUlist = file.readlines()
file.close()

file = open("NFE.txt")
NFElist = file.readlines()
file.close()

lsname = []
for line in range(0,len(pokelist)):
	lsname.append(pokelist[line][str.find(pokelist[line],' ')+1:len(pokelist[line])-1])
NFE = []
for line in range(0,len(NFElist)):
	NFE.append(NFElist[line][str.find(NFElist[line],' ')+1:len(NFElist[line])-1])
file = open("tiers.yml")
tiersYML = file.readlines()
file.close()

file = open("BL.yml")
BLYML = file.readlines()
file.close()

curTiers = ['PU' for i in range(len(pokelist))] #any pokemon not found in the list must be PU
usage = [[0,0,0,0] for i in range(len(pokelist))] #track usage across all relevant tiers [OU,UU,RU,NU]

#there's a lot of unrelated stuff in tiers.yml
for i in range(len(tiersYML)):
	if tiersYML[i] == '5th Gen:\n':
		#found the beginning of 5th gen!
		start = i
		break

#get unreleased
for i in range(start+6,len(tiersYML)):
	if tiersYML[i] == '    moves:\n':
		start = i
		break
	name = tiersYML[i][8:len(tiersYML[i])-1]
	found = False
	for j in range(0,len(lsname)):
		if name == lsname[j]:
			curTiers[j] = 'Unreleased'
			found = True
			break
	if not found:
		print name+" not found!"
		sys.exit()

#skip until you get to ubers
for i in range(start,len(tiersYML)):
	if tiersYML[i] == '  Standard OU:\n':
		#found the beginning of Ubers!
		start = i
		break

#get ubers
for i in range(start+5,len(tiersYML)):
	if tiersYML[i] == '    moves:\n':
		start = i
		break
	name = tiersYML[i][8:len(tiersYML[i])-1]
	found = False
	for j in range(0,len(lsname)):
		if name == lsname[j]:
			if (curTiers[j] == 'PU'):
			#higher tier trumps lower tier
				curTiers[j] = 'Ubers'
			found = True
			break
	if not found:
		print name+" not found!"
		sys.exit()

#skip until you get to OU
for i in range(start,len(tiersYML)):
	if tiersYML[i] == '  Standard UU:\n':
		#found the beginning of OU!
		start = i
		break

unchangedLines = [[0,start+5]] #everything before this point will be the same in the new yml file

for i in range(start+5,len(tiersYML)):
	if tiersYML[i] == '    moves:\n':
		start = i
		break
	name = tiersYML[i][8:len(tiersYML[i])-1]
	found = False
	for j in range(0,len(lsname)):
		if name == lsname[j]:
			if (curTiers[j] == 'PU'):
			#higher tier trumps lower tier
				curTiers[j] = 'OU'
			found = True
			break
	if not found:
		print name+" not found!"
		sys.exit()

#don't worry about BL yet--we'll come back for it

#skip until you get to UU
for i in range(start,len(tiersYML)):
	if tiersYML[i] == '  Standard RU:\n':
		#found the beginning of UU!
		break

unchangedLines.append([start,i+5]) #everything before this point will be the same in the new yml file
start=i

for i in range(start+5,len(tiersYML)):
	if tiersYML[i] == '    moves:\n':
		start = i
		break
	name = tiersYML[i][8:len(tiersYML[i])-1]
	found = False
	for j in range(0,len(lsname)):
		if name == lsname[j]:
			if (curTiers[j] == 'PU'):
			#higher tier trumps lower tier
				curTiers[j] = 'UU'
			found = True
			break
	if not found:
		print name+" not found!"
		sys.exit()

#don't worry about BL2 yet--we'll come back for it

#skip until you get to RU
for i in range(start,len(tiersYML)):
	if tiersYML[i] == '  Standard NU:\n':
		#found the beginning of RU!
		break

unchangedLines.append([start,i+5]) #everything before this point will be the same in the new yml file
start=i

for i in range(start+5,len(tiersYML)):
	if tiersYML[i] == '    moves:\n':
		start = i
		break
	name = tiersYML[i][8:len(tiersYML[i])-1]
	found = False
	for j in range(0,len(lsname)):
		if name == lsname[j]:
			if (curTiers[j] == 'PU'):
			#higher tier trumps lower tier
				curTiers[j] = 'RU'
			found = True
			break
	if not found:
		print name+" not found!"
		sys.exit()

unchangedLines.append([start,len(tiersYML)]) #the rest of the file will be unchanged

#read in NU list
for i in range(0,len(NUlist)):
	found = False
	name = NUlist[i][0:len(NUlist[i])-1]
	for j in range(0,len(lsname)):
		if name == lsname[j]:
			if (curTiers[j] == 'PU'):
			#higher tier trumps lower tier
				curTiers[j] = 'NU'
			found = True
			break
	if not found:
		print name+" not found!"
		sys.exit() 

#now we read in the BLs
tier = 'BL'
for i in range(1,len(BLYML)):
	if BLYML[i][0] != ' ':
		tier = BLYML[i][0:len(BLYML[i])-2]
	else:
		name = BLYML[i][8:len(BLYML[i])-1]
		found = False
		for j in range(0,len(lsname)):
			if name == lsname[j]:
				#BL trumps non-BL
				curTiers[j] = tier
				found = True
				break
		if not found:
			print name+" not found!"
			sys.exit() 

#that was the easy part. Now the fun begins. Read in the usage stats for...



#...first month's...
readTable(str(sys.argv[1])+"/Stats/Standard OU Rated.txt",0,1.0,usage) #OU
readTable(str(sys.argv[1])+"/Stats/Standard UU Rated.txt",1,1.0,usage) #UU
readTable(str(sys.argv[1])+"/Stats/Standard RU Rated.txt",2,1.0,usage) #RU
readTable(str(sys.argv[1])+"/Stats/Standard NU Rated.txt",3,1.0,usage) #NU

#...second month
readTable(str(sys.argv[2])+"/Stats/Standard OU Rated.txt",0,3.0,usage)
readTable(str(sys.argv[2])+"/Stats/Standard UU Rated.txt",1,3.0,usage)
readTable(str(sys.argv[2])+"/Stats/Standard RU Rated.txt",2,3.0,usage)
readTable(str(sys.argv[2])+"/Stats/Standard NU Rated.txt",3,3.0,usage)

#...third month
readTable(str(sys.argv[3])+"/Stats/Standard OU Rated.txt",0,20.0,usage)
readTable(str(sys.argv[3])+"/Stats/Standard UU Rated.txt",1,20.0,usage)
readTable(str(sys.argv[3])+"/Stats/Standard RU Rated.txt",2,20.0,usage)
readTable(str(sys.argv[3])+"/Stats/Standard NU Rated.txt",3,20.0,usage)


#generate three-month tables and start working on that new tier list
newTiers = ['PU' for i in range(len(pokelist))]
OU = []
UU = []
RU = []
NU = []
for i in range(0,len(usage)):
	if usage[i][0] > 0.0:
		OU.append([i,usage[i][0]])
	if usage[i][1] > 0.0:
		UU.append([i,usage[i][1]])
	if usage[i][2] > 0.0:
		RU.append([i,usage[i][2]])
	if usage[i][3] > 0.0:
		NU.append([i,usage[i][3]])
OU = sorted(OU, key=lambda OU:-OU[1])
UU = sorted(UU, key=lambda UU:-UU[1])
RU = sorted(RU, key=lambda RU:-RU[1])
NU = sorted(NU, key=lambda NU:-NU[1])

print "[B]Three-month statistics[/B]"
print "Three month usage = (20*Dec+3*Nov+1*Oct)/24"
makeTable(OU,"OU",newTiers)
makeTable(UU,"UU",newTiers)
makeTable(RU,"RU",newTiers)
makeTable(NU,"NU",newTiers)

#correct based on current tiers
poke = []
for i in range(len(curTiers)):
	#put in all the non-usage tiers
	if curTiers[i] in ['Unreleased','Ubers']:
		newTiers[i] = curTiers[i]
	elif curTiers[i] == 'BL':
		if newTiers[i] != 'OU':
			newTiers[i] = 'BL'
	elif curTiers[i] == 'BL2':
		if newTiers[i] not in ['OU','UU']:
			newTiers[i] = 'BL2'
	elif curTiers[i] == 'BL3':
		if newTiers[i] in ['NU', 'PU']:
			newTiers[i] = 'BL3'
	#now to prevent multi-tier drops
	elif curTiers[i] == 'OU':
		if newTiers[i] in ['RU','NU','PU']:
			newTiers[i] = 'UU'
	elif curTiers[i] == 'UU':
		if newTiers[i] in ['NU','PU']:
			newTiers[i] = 'RU'
	elif curTiers[i] == 'RU':
		if newTiers[i] == 'PU':
			newTiers[i] = 'NU'

	#stupid formes are stupid
	if i == 173:
		newTiers[i] = newTiers[172] #spiky pichu
	elif i in range(507,534):
		newTiers[i] = newTiers[202] #unown
	elif i in [553,554,555]:
		newTiers[i] = newTiers[352] #castform
	elif i in [551,552]:
		newTiers[i] = newTiers[413] #burmy
	elif i == 556:
		newTiers[i] = newTiers[422] #cherrim
	elif i == 557:
		newTiers[i] = newTiers[423] #shellos
	elif i == 558:
		newTiers[i] = newTiers[424] #gastrodon
	elif i == 616:
		newTiers[i] = newTiers[615] #basculin
	elif i == 622:
		newTiers[i] = newTiers[621] #darmanitan
	elif i in [653,654,655]:
		newTiers[i] = newTiers[652] #deerling
	elif i in [657,658,659]:
		newTiers[i] = newTiers[656] #sawsbuck
	elif i == 722:
		newTiers[i] = newTiers[721] #meloetta
	elif i > 723:
		newTiers[i] = newTiers[723] #genesect

	#replace names with numbers (really should have used numbers from the beginning) so it's sortable
	if newTiers[i] == 'Unreleased':
		poke.append([i,-1.0])
	elif newTiers[i] == 'Ubers':
		poke.append([i,0.0])
	elif newTiers[i] == 'OU':
		poke.append([i,1.0])
	elif newTiers[i] == 'BL':
		poke.append([i,1.5])
	elif newTiers[i] == 'UU':
		poke.append([i,2.0])
	elif newTiers[i] == 'BL2':
		poke.append([i,2.5])
	elif newTiers[i] == 'RU':
		poke.append([i,3.0])
	elif newTiers[i] == 'BL3':
		poke.append([i,3.5])
	elif newTiers[i] == 'NU':
		poke.append([i,4.0])
	elif newTiers[i] == 'PU':
		if lsname[i] not in NFE:
			poke.append([i,5.0])
		else:
			poke.append([i,5.1])

#print tier list
poke = sorted(poke, key=lambda poke:poke[1])

print "[B]Unreleased[/B]"
print "[CODE]"
print lsname[poke[0][0]]
for i in range(1,len(poke)):
	if poke[i][1] != poke[i-1][1]:
		print "[/CODE]"
		print ""
		if poke[i][1] == 0.0:
			print "[B]Ubers[/B]"
		elif poke[i][1] == 1.0:
			print "[B]OU[/B]"
		elif poke[i][1] == 1.5:
			print "[B]BL[/B]"
		elif poke[i][1] == 2.0:
			print "[B]UU[/B]"
		elif poke[i][1] == 2.5:
			print "[B]BL2[/B]" 
		elif poke[i][1] == 3.0:
			print "[B]RU[/B]"
		elif poke[i][1] == 3.5:
			print "[B]BL3[/B]"
		elif poke[i][1] == 4.0:
			print "[B]NU[/B]"
		elif poke[i][1] == 5.0:
			print "[B]PU[/B]"
			print 'Note that "PU" is not a real tier and will NOT be supported on the simulator. I post the list here just as a point of reference--these pokemon are the NU of NU.'
			print "[HIDE]"
		elif poke[i][1] == 5.1:
			print "NFEs:"	
		print "[CODE]"
	if poke[i][0] in [0,173]+range(507,534)+range(551,559)+[616,622,653,654,655,657,658,659,722,724,725,726,727]:
		continue
	printme=lsname[poke[i][0]]
	if newTiers[poke[i][0]] != curTiers[poke[i][0]]:
		#if newTiers[poke[i][0]] != 'PU':
		printme="[B]"+printme
		if newTiers[poke[i][0]] == 'OU':
			printme=printme+" up"
		elif newTiers[poke[i][0]] == 'UU':
			if curTiers[poke[i][0]] == 'OU':
				printme=printme+" down"
			else:
				printme=printme+" up"
		elif newTiers[poke[i][0]] == 'RU':
			if curTiers[poke[i][0]] in ['BL3','NU','PU']:
				printme=printme+" up"
			else:
				printme=printme+" down"
		elif newTiers[poke[i][0]] == 'NU':
			if curTiers[poke[i][0]] == 'RU':
				printme=printme+" down"
			else:
				printme=printme+" up"
		else:
			printme=printme+" down"
		#if newTiers[poke[i][0]] != 'PU':
		printme=printme+" from "+curTiers[poke[i][0]]+"[/B]"
	print printme

print "[/CODE][/HIDE]"

#write new tier yml
outfile=open('newTiers.yml','w')
for i in range(unchangedLines[0][0],unchangedLines[0][1]):
	outfile.write(str(tiersYML[i]))
for start in range(0,len(poke)):
	if poke[start][1] == 1.0:
		break
for i in range(start,len(poke)):
	if poke[i][1] >= 2.0:
		start = i
		break
	outfile.write("      - "+str(lsname[poke[i][0]])+"\n")
for i in range(unchangedLines[1][0],unchangedLines[1][1]):
	outfile.write(str(tiersYML[i]))
for i in range(start,len(poke)):
	if poke[i][1] >= 3.0:
		start = i
		break
	outfile.write("      - "+str(lsname[poke[i][0]])+"\n")
for i in range(unchangedLines[2][0],unchangedLines[2][1]):
	outfile.write(str(tiersYML[i]))
for i in range(start,len(poke)):
	if poke[i][1] >= 4.0:
		start = i
		break
	outfile.write("      - "+str(lsname[poke[i][0]])+"\n")
for i in range(unchangedLines[3][0],unchangedLines[3][1]):
	outfile.write(str(tiersYML[i]))
outfile.close()

#write new NU txt
outfile=open('newNU.txt','w')
for i in range (start,len(poke)):
	if poke[i][1] >= 5.0:
		start = i
		break
	outfile.write(str(lsname[poke[i][0]])+"\n")
outfile.close()
