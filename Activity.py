#!/usr/bin/python
import string
import sys
filename = str(sys.argv[1])
file = open(filename)
log = file.readlines()

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

outname = "Activity/"+tier+" "+rated+".txt"
outfile=open(outname,'a')
idx=string.rfind(filename,'Logs/')
date=filename[idx+13:idx+15]
hour=filename[idx+16:idx+18]
minute=filename[idx+19:idx+21]
second=filename[idx+22:idx+24]
outfile.write(date+','+hour+','+minute+','+second+'\n')
outfile.close()
