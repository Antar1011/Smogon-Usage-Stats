#!/usr/bin/python
import string
import sys

filename = str(sys.argv[1])
file = open(filename)
lines = file.readlines()
tier=filename[str.rfind(filename,'/')+1:len(filename)-4]
#print "."+tier+"."

#we're going to do this hourly
bin = [0 for i in range(31*24)]

for line in lines:	
	day=eval(line[0:2])
	hour=eval(line[3:5])
	#minute=eval(line[6:8])
	#second=eval(line[9:11])
	
	idx = day*24+hour
	bin[idx]=bin[idx]+1

for i in range(31*24):
	print 1.0*i/24,bin[i]
