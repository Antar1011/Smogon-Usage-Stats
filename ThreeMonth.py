#!/usr/bin/python
import string
import sys

file = open("pokemons.txt")
pokelist = file.readlines()
file.close()

lsname = []
for line in range(0,len(pokelist)):
	lsname.append(pokelist[line][str.find(pokelist[line],' ')+1:len(pokelist[line])-1])

usage = [0 for i in range(len(pokelist))] #track usage across all three tiers

#...first month OU
filename = str(sys.argv[1])
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
	usage[i] = usage[i]+6.0*tempUsage[i]/sum(tempUsage)/24



#...second month's OU
filename = str(sys.argv[2])
file = open(filename)
table=file.readlines()
file.close()

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
	usage[i] = usage[i]+3.0*6.0*tempUsage[i]/sum(tempUsage)/24

#...third month's OU
filename = str(sys.argv[3])
file = open(filename)
table=file.readlines()
file.close()

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
	usage[i] = usage[i]+20.0*6.0*tempUsage[i]/sum(tempUsage)/24


#generate three-month table
OU = []
for i in range(0,len(usage)):
	if usage[i] > 0.0:
		OU.append([i,usage[i]])
OU = sorted(OU, key=lambda OU:-OU[1])

print "[HIDE=OU][CODE]"
print "Three-month usage for [insert tier name here]"
print " + ---- + --------------- + ------- + "
print " | Rank | Pokemon         | Percent | "
print " + ---- + --------------- + ------- + "
print ' [B]| %-4d | %-15s | %6.3f%% |' % (1,lsname[OU[0][0]],OU[0][1]*100)
for i in range(1,len(OU)):
	if OU[i][1] < 0.0340636711:
		start = i
		break
	print ' | %-4d | %-15s | %6.3f%% |' % (i+1,lsname[OU[i][0]],100.0*OU[i][1])
print '[/B] | %-4d | %-15s | %6.3f%% |' % (i+1,lsname[OU[i][0]],100.0*OU[i][1])
for i in range(start+1,len(OU)):
	print ' | %-4d | %-15s | %6.3f%% |' % (i+1,lsname[OU[i][0]],100.0*OU[i][1])
print " + ---- + --------------- + ------- +[/CODE][/HIDE]"
