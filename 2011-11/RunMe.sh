SUBJECT="November Usage Stats"
EMAILMESSAGE="/tmp/emailmessage.txt"
EMAIL="antar05@gmail.com"

mkdir Raw
mkdir Stats

#rm Raw/*
rm Stats/*

maxjobs=1 #set to number of multiprocessors

for j in Logs/*
do
	for  i in "$j"/*
	do
		#jobcnt=(`jobs -p`)
		#while [ ${#jobcnt[@]} -ge $maxjobs ]
		#do
		#	jobcnt=(`jobs -p`)
		#done
		echo Processing $i
		python ../LogReaderOnCrack.py "$i"
	done
done

#serial version:
#	for j in "$i"/*
#	do
#		echo Processing $j
#		python LogReader.py "$j"
#	done




#stupid tier name changes--gotta consolidate...
#cat "Raw/BW LC Rated.txt" >> "Raw/Standard LC Rated.txt"
#cat "Raw/BW LC Unrated.txt" >> "Raw/Standard LC Unrated.txt"
#cat "Raw/BW OU Rated.txt" >> "Raw/Standard OU Rated.txt"
#cat "Raw/BW OU Unrated.txt" >> "Raw/Standard OU Unrated.txt"
#cat "Raw/BW UU Rated.txt" >> "Raw/Standard UU Rated.txt"
#cat "Raw/BW UU Unrated.txt" >> "Raw/Standard UU Unrated.txt"
#cat "Raw/BW RU Rated.txt" >> "Raw/Standard RU Rated.txt"
#cat "Raw/BW RU Unrated.txt" >> "Raw/Standard RU Unrated.txt"
#cat "Raw/BW Uber Rated.txt" >> "Raw/Standard Ubers Rated.txt"
#cat "Raw/BW Uber Unrated.txt" >> "Raw/Standard Ubers Unrated.txt"
#rm Raw/BW*.txt

echo Compiling Standard Stats...
for i in Raw/*; do python ../StatCounterOnCrack.py "$i" > "Stats/${i/Raw}" ; done

echo Compiling Lead and 1337 stats...
mkdir Stats/Leads
python ../StatCounterLeadsOnCrack.py "Raw/Standard UU Rated.txt" > "Stats/Leads/Standard UU Rated.txt"
python ../StatCounterLeadsOnCrack.py "Raw/Standard RU Rated.txt" > "Stats/Leads/Standard RU Rated.txt"
python ../StatCounterLeadsOnCrack.py "Raw/Standard NU Rated.txt" > "Stats/Leads/Standard NU Rated.txt"
python ../StatCounterLeadsOnCrack.py "Raw/Standard Ubers Rated.txt" > "Stats/Leads/Standard Ubers Rated.txt"
python ../StatCounterLeadsOnCrack.py "Raw/Standard LC Rated.txt" > "Stats/Leads/Standard LC Rated.txt"
python ../StatCounterLeadsOnCrack.py "Raw/Standard OU Rated.txt" > "Stats/Leads/Standard OU Rated.txt"

mkdir Stats/1337
python ../StatCounter1337OnCrack.py "Raw/Standard OU Rated.txt" ratings/OU.txt > "Stats/1337/Standard OU Rated.txt"
python ../StatCounter1337OnCrack.py "Raw/Standard UU Rated.txt" ratings/UU.txt > "Stats/1337/Standard UU Rated.txt"
python ../StatCounter1337OnCrack.py "Raw/Standard RU Rated.txt" ratings/RU.txt > "Stats/1337/Standard RU Rated.txt"
python ../StatCounter1337OnCrack.py "Raw/Standard NU Rated.txt" ratings/NU.txt > "Stats/1337/Standard NU Rated.txt"
python ../StatCounter1337OnCrack.py "Raw/Standard Ubers Rated.txt" ratings/Ubers.txt > "Stats/1337/Standard Ubers Rated.txt"
python ../StatCounter1337OnCrack.py "Raw/Standard LC Rated.txt" ratings/LC.txt > "Stats/1337/Standard LC Rated.txt"

echo Making the Thread...

echo [Intro goes here] > Standard\ Stats.txt
echo >> Standard\ Stats.txt 
echo [HIDE=Standard OU Rated][CODE]  >> Standard\ Stats.txt 
cat Stats/Standard\ OU\ Rated.txt >> Standard\ Stats.txt
echo [/CODE][/HIDE] >> Standard\ Stats.txt
echo >> Standard\ Stats.txt
echo [HIDE=Standard UU Rated][CODE]  >> Standard\ Stats.txt 
cat Stats/Standard\ UU\ Rated.txt >> Standard\ Stats.txt
echo [/CODE][/HIDE] >> Standard\ Stats.txt
echo >> Standard\ Stats.txt
echo [HIDE=Standard RU Rated][CODE]  >> Standard\ Stats.txt 
cat Stats/Standard\ RU\ Rated.txt >> Standard\ Stats.txt
echo [/CODE][/HIDE] >> Standard\ Stats.txt
echo >> Standard\ Stats.txt
echo [HIDE=Standard NU Rated][CODE]  >> Standard\ Stats.txt 
cat Stats/Standard\ NU\ Rated.txt >> Standard\ Stats.txt
echo [/CODE][/HIDE] >> Standard\ Stats.txt
echo >> Standard\ Stats.txt
echo [HIDE=Standard Ubers Rated][CODE]  >> Standard\ Stats.txt 
cat Stats/Standard\ Ubers\ Rated.txt >> Standard\ Stats.txt
echo [/CODE][/HIDE] >> Standard\ Stats.txt
echo >> Standard\ Stats.txt
echo [HIDE=Standard LC Rated][CODE]  >> Standard\ Stats.txt 
cat Stats/Standard\ LC\ Rated.txt >> Standard\ Stats.txt
echo [/CODE][/HIDE] >> Standard\ Stats.txt

echo [B]Lead Usage[/B] > Lead\ Stats.txt
echo >> Lead\ Stats.txt
echo [HIDE=OU][CODE] >> Lead\ Stats.txt
cat Stats/Leads/Standard\ OU\ Rated.txt >> Lead\ Stats.txt
echo [/CODE][/HIDE] >> Lead\ Stats.txt
echo >> Lead\ Stats.txt
echo [HIDE=UU][CODE] >> Lead\ Stats.txt
cat Stats/Leads/Standard\ UU\ Rated.txt >> Lead\ Stats.txt
echo [/CODE][/HIDE] >> Lead\ Stats.txt
echo >> Lead\ Stats.txt
echo [HIDE=RU][CODE] >> Lead\ Stats.txt
cat Stats/Leads/Standard\ RU\ Rated.txt >> Lead\ Stats.txt
echo [/CODE][/HIDE] >> Lead\ Stats.txt
echo >> Lead\ Stats.txt
echo [HIDE=NU][CODE] >> Lead\ Stats.txt
cat Stats/Leads/Standard\ NU\ Rated.txt >> Lead\ Stats.txt
echo [/CODE][/HIDE] >> Lead\ Stats.txt
echo >> Lead\ Stats.txt
echo [HIDE=Ubers][CODE] >> Lead\ Stats.txt
cat Stats/Leads/Standard\ Ubers\ Rated.txt >> Lead\ Stats.txt
echo [/CODE][/HIDE] >> Lead\ Stats.txt
echo >> Lead\ Stats.txt
echo [HIDE=LC][CODE] >> Lead\ Stats.txt
cat Stats/Leads/Standard\ LC\ Rated.txt >> Lead\ Stats.txt
echo [/CODE][/HIDE] >> Lead\ Stats.txt

echo [b]1337 stats![/b] > 1337\ Stats.txt
echo This data only takes into account teams whose user has a current rating--as of 12/1--of 1337 or higher. In tiers where there were not enough players with a rating that high, I lowered the cutoff as specified. >> 1337\ Stats.txt
echo >> 1337\ Stats.txt
echo [HIDE=OU][CODE] >> 1337\ Stats.txt
cat Stats/1337/Standard\ OU\ Rated.txt >> 1337\ Stats.txt
echo [/CODE][/HIDE] >> 1337\ Stats.txt
echo >> 1337\ Stats.txt
echo [HIDE=UU][CODE] >> 1337\ Stats.txt
cat Stats/1337/Standard\ UU\ Rated.txt >> 1337\ Stats.txt
echo [/CODE][/HIDE] >> 1337\ Stats.txt
echo >> 1337\ Stats.txt
echo [HIDE=RU][CODE] >> 1337\ Stats.txt
cat Stats/1337/Standard\ RU\ Rated.txt >> 1337\ Stats.txt
echo [/CODE][/HIDE] >> 1337\ Stats.txt
echo >> 1337\ Stats.txt
echo [HIDE=NU][CODE] >> 1337\ Stats.txt
cat Stats/1337/Standard\ NU\ Rated.txt >> 1337\ Stats.txt
echo [/CODE][/HIDE] >> 1337\ Stats.txt
echo >> 1337\ Stats.txt
echo [HIDE=Ubers][CODE] >> 1337\ Stats.txt
cat Stats/1337/Standard\ Ubers\ Rated.txt >> 1337\ Stats.txt
echo [/CODE][/HIDE] >> 1337\ Stats.txt
echo >> 1337\ Stats.txt
echo [HIDE=LC][CODE] >> 1337\ Stats.txt
cat Stats/1337/Standard\ LC\ Rated.txt >> 1337\ Stats.txt
echo [/CODE][/HIDE] >> 1337\ Stats.txt

echo "Stats compiled!"> $EMAILMESSAGE
echo "" >>$EMAILMESSAGE
echo "-REFO" >>$EMAILMESSAGE
mail -s "$SUBJECT" "$EMAIL" < $EMAILMESSAGE

