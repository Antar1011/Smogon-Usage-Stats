#!/usr/bin/python

import sys
from common import readTable

old = readTable(sys.argv[1])
new = readTable(sys.argv[2])

diff = {}
for poke in new.keys():
	if poke not in old.keys():
		old[poke]=0.0
	diff[poke]=new[poke]-old[poke]

pokes=[]
for i in diff.keys():
	pokes.append([i,diff[i]])

pokes=sorted(pokes, key=lambda pokes:-pokes[1])
print " + ------------------ + --------- + "
print " | Pokemon            | Diff (%)  | "
print " + ------------------ + --------- + "

for i in range(0,len(pokes)):
	if abs(pokes[i][1]) > 0.001:
		print ' | %-18s | %+8.5f%% | ' % (pokes[i][0],pokes[i][1]*100.0)

print " + ------------------ + --------- + "
