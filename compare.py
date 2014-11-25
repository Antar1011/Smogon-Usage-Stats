#!/usr/bin/python

import sys
from common import readTable

old,nold = readTable(sys.argv[1])
new,nnew = readTable(sys.argv[2])

diff = {}
for poke in new.keys():
	if poke not in old.keys():
		old[poke]=0.0
	diff[poke]=new[poke]-old[poke]

pokes=[]
for i in diff.keys():
	pokes.append([i,diff[i]])

pokes=sorted(pokes, key=lambda pokes:-pokes[1])
if (nold != nnew):
	if (nold < nnew):
		printme = " Up %5.2f%%" % (100*float(nnew-nold)/nold)
	else:
		printme = " Down %5.2f%%" % (100*float(nold-nnew)/nold)
	print printme
print " + ------------------ + --------- + "
print " | Pokemon            | Diff (%)  | "
print " + ------------------ + --------- + "

for i in range(0,len(pokes)):
	if abs(pokes[i][1]) > 0.001:
		print ' | %-18s | %+8.5f%% | ' % (pokes[i][0],pokes[i][1]*100.0)

print " + ------------------ + --------- + "
