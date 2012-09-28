#!/usr/bin/python
#This script is designed to generate a UU banlist (OU list) for an arbitrary tier
#(like Dream World, Little Cup or Ubers) using usage tables from the previous three
#months.
#
#Syntax: python OtherOU.py Month1Table Month2Table Month3Table
#where MonthNTable is the filename of the usage table
 
import string
import sys
import json
import cPickle as pickle

def keyify(s):
	sout = ''
	for c in s:
		if c in string.uppercase:
			sout = sout + c.lower()
		elif c in string.lowercase + '1234567890':
			sout = sout + c
	return sout

def readTable(filename,col,weight,usage):
	file = open(filename)
	table=file.readlines()
	file.close()

	#'real' usage screwed me over--I can't take total count from header
	#using percentages is a bad idea because of roundoff

	tempUsage = {} #really dumb that I have to do this

	for i in range(6,len(table)):
		name = table[i][10:29]
	
		if (name[0] == '-'):
			break

		while name[len(name)-1] == ' ': 
			#remove extraneous spaces
			name = name[0:len(name)-1]
	
		count = table[i][31:38]
		while count[len(count)-1] == ' ':
			#remove extraneous spaces
			count = count[0:len(count)-1]
			tempUsage[keyify(name)]=float(count)

	for i in tempUsage:
		if i not in usage:
			usage[i]=[0,0,0,0]
		if i != 'empty':
			usage[i][col] = usage[i][col]+weight*6.0*tempUsage[i]/sum(tempUsage.values())/24

def makeTable(table):
	banlist = []

	print "[CODE]"
	print "Three-month usage"
	print " + ---- + ------------------ + ------- + "
	print " | Rank | Pokemon            | Percent | "
	print " + ---- + ------------------ + ------- + "
	print ' [B]| %-4d | %-18s | %6.3f%% |' % (1,keyLookup[table[0][0]],table[0][1]*100)
	for i in range(1,len(table)):
		if table[i][1] < 0.0340636711:
			start = i
			break
		print ' | %-4d | %-18s | %6.3f%% |' % (i+1,keyLookup[table[i][0]],100.0*table[i][1])
		banlist.append(keyLookup[table[i][0]])
	print '[/B] | %-4d | %-18s | %6.3f%% |' % (i+1,keyLookup[table[i][0]],100.0*table[i][1])
	for i in range(start+1,len(table)):
		print ' | %-4d | %-18s | %6.3f%% |' % (i+1,keyLookup[table[i][0]],100.0*table[i][1])
	print " + ---- + --------------- + ------- +[/CODE]"
	return banlist


file = open('keylookup.pickle')
keyLookup = pickle.load(file)
file.close()

usage = {} #track usage across all relevant tiers [OU,UU,RU,NU]

#...first month's...
readTable(str(sys.argv[1]),0,1.0,usage)

#...second month
readTable(str(sys.argv[2]),0,3.0,usage)

#...third month
readTable(str(sys.argv[3]),0,20.0,usage)

#generate three-month table
OU = []

for i in usage:
	if usage[i][0] > 0.0:
		OU.append([i,usage[i][0]])
OU = sorted(OU, key=lambda OU:-OU[1])


print "[B]Three-month statistics[/B]"
print "Three month usage = (20*LastMonth+3*OneMonthAgo+1*TwoMonthsAgo)/24"
banlist = makeTable(OU)

banlist = sorted(banlist, key=lambda banlist:banlist)

#print banlist
print
print '[B]UU Banlist: [/B]'
print ', '.join(banlist)
