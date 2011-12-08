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

#get info on the trainers involved
t = []
skip = 0
if oldWay == False:
	for line in range(1,len(log)):
		if log[line][0:19] == '<div class="Teams">':
			for x in range(0,2):
				trainer = log[line+x][50:string.rfind(log[line+x],"'s team:")]
				if string.find(trainer,"send out") > -1:
					print trainer+" is a dick."
					sys.exit()
				t.append(trainer)
			break

if (line == len(log)) or oldWay == True: #it's an old log, so find pokes the old way
	#find all "sent out" messages
	for line in range(5,len(log)):
		if log[line][0:21] == '<div class="SendOut">':
			ttemp = log[line][21:string.find(log[line],' sent out ')]

			#determine whether this entry is already in the list
			match = 0
			for i in range(0,len(t)):
				if (t[i] == ttemp):
					match = 1
					break
			if match == 0:
				t.append(ttemp)
		if len(t) == 2:
			break

if len(t)<2:
	print "Skipping "+filename
	sys.exit()

anonymized=[]
for line in range(1,len(log)):
	idx=-1
	if log[line][0:21] == '<div class="SendOut">':
		idx = 0
		ttemp = log[line][21:string.find(log[line],' sent out ')]
		if ttemp == t[0]:
			i=0
		else:
			i=1
		atemp = log[line][0:string.find(log[line],t[i])]+'-Trainer '+str(i)+'-'+log[line][string.find(log[line],' sent out '):len(log[line])]
	else:
		idx = str.find(log[line],t[0])
		i=0
		if idx == -1:
			idx = str.find(log[line],t[1])
			i=1
		if idx > -1:
			atemp = log[line][0:idx]+'-Trainer '+str(i)+'-'+log[line][idx+len(t[i]):len(log[line])]
		if i==0:
			#gotta check to make sure both trainer's names aren't in the line
			idx = str.find(atemp,t[1])
			if idx > -1:
				at2 = atemp
				atemp = at2[0:idx]+'-Trainer '+str(1)+'-'+at2[idx+len(t[1]):len(at2)]
			else:
				idx = 0
	if idx == -1:
		atemp = log[line]
	anonymized.append(atemp)

outname = "Anonymized/"+filename
outfile=open(outname,'w')
for line in anonymized:
	outfile.write(line)
outfile.close()
