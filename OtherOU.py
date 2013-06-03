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
from common import keyify,getUsage

def makeTable(table):
	banlist = []

	print "[CODE]"
	print "Three-month usage"
	print " + ---- + ------------------ + ------- + "
	print " | Rank | Pokemon            | Percent | "
	print " + ---- + ------------------ + ------- + "
	print ' [B]| %-4d | %-18s | %6.3f%% |' % (1,keyLookup[table[0][0]],table[0][1]*100)
	banlist.append(keyLookup[table[0][0]])
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
getUsage(str(sys.argv[1]),0,1.0,usage)

#...second month
getUsage(str(sys.argv[2]),0,3.0,usage)

#...third month
getUsage(str(sys.argv[3]),0,20.0,usage)

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
