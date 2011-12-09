#!/usr/bin/python
import string
import sys

daysInMonth = 29

mode = '-MonthLong'
if len(sys.argv) > 2:
	mode = sys.argv[2]
	if mode not in ['-MonthLong','-Daily','-Hourly']:
		print 'Invalid mode. Valid options are:'
		for mode in ['-MonthLong','-Daily','-Hourly']:
			print mode
		sys.exit()

filename = str(sys.argv[1])
file = open(filename)
lines = file.readlines()
tier=filename[str.rfind(filename,'/')+1:len(filename)-4]
#print "."+tier+"."

if mode == '-MonthLong':
	#hourly bin for the whole month
	bin = [0 for i in range(31*24)]
	binSize = 3600
elif mode == '-Hourly':
	#hourly bin
	bin = [0 for i in range(24)]
	binSize = 3600*daysInMonth
elif mode == '-Daily':
	#daily bin
	bin = [0 for i in range(32)]
	binSize = 3600*24

for line in lines:	
	day=int(line[0:2])
	hour=int(line[3:5])
	#minute=int(line[6:8])
	#second=int(line[9:11])
	
	if mode == '-MonthLong':
		idx = day*24+hour
	elif mode == '-Hourly':
		idx = hour
	elif mode == '-Daily':
		idx = day
	if day != 19 or mode != '-Hourly':
		bin[idx]=bin[idx]+1

for i in range(len(bin)):
	if mode == '-MonthLong':
		out=str(1.0*(i+1)/24)+"\t"+str(bin[i])+"\t"
	elif mode == '-Hourly':
		out=str(i)+"\t"+str(1.0*bin[i]/daysInMonth)+"\t"
	elif mode == '-Daily':
		out=str(i)+"\t"+str(1.0*bin[i])+"\t"
	if bin[i]==0:
		out=out+"---"
	else:
		out=out+str(1.0*binSize/bin[i])
	print out
