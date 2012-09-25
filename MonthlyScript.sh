echo Compiling Stats...
mkdir Stats
mkdir Stats/Leads
echo Compiling Usage Stats and Metagame Analyses...
for tier in "balancedhackmons" "cap" "challengecup" "dwou" "dwubers" "glitchmons" "hackmons" "lc" "nu" "ou" "oususpecttest" "randombattle" "ru" "ubers" "uu"
do
	python ../StatCounterOnCrackv3.py Raw/$tier.txt &
	python ../StatCounterLeadsOnCrackv2.py Raw/$tier.txt > Stats/Leads/$tier.txt &
	wait
done

echo Making the Thread...

echo [HIDE=Standard OU Rated][CODE]  > Standard\ Stats.txt 
cat Stats/ou.txt >> Standard\ Stats.txt
echo [/CODE][/HIDE] >> Standard\ Stats.txt
echo >> Standard\ Stats.txt
echo [HIDE=Standard UU Rated][CODE]  >> Standard\ Stats.txt 
cat Stats/uu.txt >> Standard\ Stats.txt
echo [/CODE][/HIDE] >> Standard\ Stats.txt
echo >> Standard\ Stats.txt
echo [HIDE=Standard RU Rated][CODE]  >> Standard\ Stats.txt 
cat Stats/ru.txt >> Standard\ Stats.txt
echo [/CODE][/HIDE] >> Standard\ Stats.txt
echo >> Standard\ Stats.txt
echo [HIDE=Standard NU Rated][CODE]  >> Standard\ Stats.txt 
cat Stats/nu.txt >> Standard\ Stats.txt
echo [/CODE][/HIDE] >> Standard\ Stats.txt
echo >> Standard\ Stats.txt
echo [HIDE=Standard Ubers Rated][CODE]  >> Standard\ Stats.txt 
cat Stats/ubers.txt >> Standard\ Stats.txt
echo [/CODE][/HIDE] >> Standard\ Stats.txt
echo >> Standard\ Stats.txt
echo [HIDE=Standard LC Rated][CODE]  >> Standard\ Stats.txt 
cat Stats/lc.txt >> Standard\ Stats.txt
echo [/CODE][/HIDE] >> Standard\ Stats.txt
echo >> Standard\ Stats.txt
echo [B]Additional metagames[/B] >> Standard\ Stats.txt
echo [HIDE=Dream World OU Rated][CODE]  >> Standard\ Stats.txt 
cat Stats/dwou.txt >> Standard\ Stats.txt
echo [/CODE][/HIDE] >> Standard\ Stats.txt
echo >> Standard\ Stats.txt
echo [HIDE=Dream World Ubers Rated][CODE]  >> Standard\ Stats.txt 
cat Stats/dwubers.txt >> Standard\ Stats.txt
echo [/CODE][/HIDE] >> Standard\ Stats.txt
echo >> Standard\ Stats.txt
echo [HIDE=CAP Rated][CODE]  >> Standard\ Stats.txt 
cat Stats/cap.txt >> Standard\ Stats.txt
echo [/CODE][/HIDE] >> Standard\ Stats.txt
echo >> Standard\ Stats.txt
echo [HIDE=Hackmons Rated][CODE]  >> Standard\ Stats.txt 
cat Stats/hackmons.txt >> Standard\ Stats.txt
echo [/CODE][/HIDE] >> Standard\ Stats.txt
echo >> Standard\ Stats.txt
echo [HIDE=Balanced Hackmons Rated][CODE]  >> Standard\ Stats.txt 
cat Stats/balancedhackmons.txt >> Standard\ Stats.txt
echo [/CODE][/HIDE] >> Standard\ Stats.txt
echo >> Standard\ Stats.txt
echo [HIDE=Glitchmons Rated][CODE]  >> Standard\ Stats.txt 
cat Stats/glitchmons.txt >> Standard\ Stats.txt
echo [/CODE][/HIDE] >> Standard\ Stats.txt
echo [HIDE=OU Suspect Test][CODE]  >> Standard\ Stats.txt 
cat Stats/oususpecttest.txt >> Standard\ Stats.txt
echo [/CODE][/HIDE] >> Standard\ Stats.txt

echo [B]Lead Usage[/B] > Lead\ Stats.txt
echo >> Lead\ Stats.txt
echo "[HIDE=OU][CODE]" >> Lead\ Stats.txt
cat Stats/Leads/ou.txt >> Lead\ Stats.txt
echo [/CODE][/HIDE] >> Lead\ Stats.txt
echo >> Lead\ Stats.txt
echo "[HIDE=UU][CODE]" >> Lead\ Stats.txt
cat Stats/Leads/uu.txt >> Lead\ Stats.txt
echo [/CODE][/HIDE] >> Lead\ Stats.txt
echo >> Lead\ Stats.txt
echo "[HIDE=RU][CODE]" >> Lead\ Stats.txt
cat Stats/Leads/ru.txt >> Lead\ Stats.txt
echo [/CODE][/HIDE] >> Lead\ Stats.txt
echo >> Lead\ Stats.txt
echo "[HIDE=NU][CODE]" >> Lead\ Stats.txt
cat Stats/Leads/nu.txt >> Lead\ Stats.txt
echo [/CODE][/HIDE] >> Lead\ Stats.txt
echo >> Lead\ Stats.txt
echo "[HIDE=Ubers][CODE]" >> Lead\ Stats.txt
cat Stats/Leads/ubers.txt >> Lead\ Stats.txt
echo [/CODE][/HIDE] >> Lead\ Stats.txt
echo >> Lead\ Stats.txt
echo "[HIDE=LC][CODE]" >> Lead\ Stats.txt
cat Stats/Leads/lc.txt >> Lead\ Stats.txt
echo [/CODE][/HIDE] >> Lead\ Stats.txt
echo >> Lead\ Stats.txt
echo [B]Additional metagames[/B] >> Lead\ Stats.txt
echo "[HIDE=DW OU][CODE]"  >> Lead\ Stats.txt 
cat Stats/Leads/dwou.txt >> Lead\ Stats.txt
echo [/CODE][/HIDE] >> Lead\ Stats.txt
echo >> Lead\ Stats.txt
echo "[HIDE=DW Ubers][CODE]"  >> Lead\ Stats.txt 
cat Stats/Leads/dwubers.txt >> Lead\ Stats.txt
echo [/CODE][/HIDE] >> Lead\ Stats.txt
echo >> Lead\ Stats.txt
echo "[HIDE=CAP][CODE]"  >> Lead\ Stats.txt 
cat Stats/Leads/cap.txt >> Lead\ Stats.txt
echo [/CODE][/HIDE] >> Lead\ Stats.txt
echo >> Lead\ Stats.txt
echo "[HIDE=Hackmons][CODE]"  >> Lead\ Stats.txt 
cat Stats/Leads/hackmons.txt >> Lead\ Stats.txt
echo [/CODE][/HIDE] >> Lead\ Stats.txt
echo >> Lead\ Stats.txt
echo "[HIDE=Balanced Hackmons][CODE]"  >> Lead\ Stats.txt 
cat Stats/Leads/balancedhackmons.txt >> Lead\ Stats.txt
echo [/CODE][/HIDE] >> Lead\ Stats.txt
echo >> Lead\ Stats.txt
echo "[HIDE=Glitchmons][CODE]"  >> Lead\ Stats.txt 
cat Stats/Leads/glitchmons.txt >> Lead\ Stats.txt
echo [/CODE][/HIDE] >> Lead\ Stats.txt
echo >> Lead\ Stats.txt
echo "[HIDE=OU Suspect Test][CODE]"  >> Lead\ Stats.txt 
cat Stats/Leads/oususpecttest.txt >> Lead\ Stats.txt
echo [/CODE][/HIDE] >> Lead\ Stats.txt
echo >> Lead\ Stats.txt

echo [B]Metagame Analyses[/B] > Metagame\ Analyses.txt
echo >> Metagame\ Analyses.txt
echo "[HIDE=OU][CODE]" >> Metagame\ Analyses.txt
cat Stats/metagame/ou.txt >> Metagame\ Analyses.txt
echo [/CODE][/HIDE] >> Metagame\ Analyses.txt
echo >> Metagame\ Analyses.txt
echo "[HIDE=UU][CODE]" >> Metagame\ Analyses.txt
cat Stats/metagame/uu.txt >> Metagame\ Analyses.txt
echo [/CODE][/HIDE] >> Metagame\ Analyses.txt
echo >> Metagame\ Analyses.txt
echo "[HIDE=RU][CODE]" >> Metagame\ Analyses.txt
cat Stats/metagame/ru.txt >> Metagame\ Analyses.txt
echo [/CODE][/HIDE] >> Metagame\ Analyses.txt
echo >> Metagame\ Analyses.txt
echo "[HIDE=NU][CODE]" >> Metagame\ Analyses.txt
cat Stats/metagame/nu.txt >> Metagame\ Analyses.txt
echo [/CODE][/HIDE] >> Metagame\ Analyses.txt
echo >> Metagame\ Analyses.txt
echo "[HIDE=Ubers][CODE]" >> Metagame\ Analyses.txt
cat Stats/metagame/ubers.txt >> Metagame\ Analyses.txt
echo [/CODE][/HIDE] >> Metagame\ Analyses.txt
echo >> Metagame\ Analyses.txt
echo "[HIDE=LC][CODE]" >> Metagame\ Analyses.txt
cat Stats/metagame/lc.txt >> Metagame\ Analyses.txt
echo [/CODE][/HIDE] >> Metagame\ Analyses.txt
echo >> Metagame\ Analyses.txt
echo [B]Additional metagames[/B] >> Metagame\ Analyses.txt
echo "[HIDE=DW OU][CODE]"  >> Metagame\ Analyses.txt 
cat Stats/metagame/dwou.txt >> Metagame\ Analyses.txt
echo [/CODE][/HIDE] >> Metagame\ Analyses.txt
echo >> Metagame\ Analyses.txt
echo "[HIDE=DW Ubers][CODE]"  >> Metagame\ Analyses.txt 
cat Stats/metagame/dwubers.txt >> Metagame\ Analyses.txt
echo [/CODE][/HIDE] >> Metagame\ Analyses.txt
echo >> Metagame\ Analyses.txt
echo "[HIDE=CAP][CODE]"  >> Metagame\ Analyses.txt 
cat Stats/metagame/cap.txt >> Metagame\ Analyses.txt
echo [/CODE][/HIDE] >> Metagame\ Analyses.txt
echo >> Metagame\ Analyses.txt
echo "[HIDE=Hackmons][CODE]"  >> Metagame\ Analyses.txt 
cat Stats/metagame/hackmons.txt >> Metagame\ Analyses.txt
echo [/CODE][/HIDE] >> Metagame\ Analyses.txt
echo >> Metagame\ Analyses.txt
echo "[HIDE=Balanced Hackmons][CODE]"  >> Metagame\ Analyses.txt 
cat Stats/metagame/balancedhackmons.txt >> Metagame\ Analyses.txt
echo [/CODE][/HIDE] >> Metagame\ Analyses.txt
echo >> Metagame\ Analyses.txt
echo "[HIDE=Glitchmons][CODE]"  >> Metagame\ Analyses.txt 
cat Stats/metagame/glitchmons.txt >> Metagame\ Analyses.txt
echo [/CODE][/HIDE] >> Metagame\ Analyses.txt
echo >> Metagame\ Analyses.txt
echo "[HIDE=OU Suspect Test][CODE]"  >> Metagame\ Analyses.txt 
cat Stats/metagame/oususpecttest.txt >> Metagame\ Analyses.txt
echo [/CODE][/HIDE] >> Metagame\ Analyses.txt
echo >> Metagame\ Analyses.txt
echo "[HIDE=Randbats][CODE]"  >> Metagame\ Analyses.txt 
cat Stats/metagame/randombattle.txt >> Metagame\ Analyses.txt
echo [/CODE][/HIDE] >> Metagame\ Analyses.txt
echo >> Metagame\ Analyses.txt
echo "[HIDE=Challenge Cup][CODE]"  >> Metagame\ Analyses.txt 
cat Stats/metagame/challengecup.txt >> Metagame\ Analyses.txt
echo [/CODE][/HIDE] >> Metagame\ Analyses.txt
echo >> Metagame\ Analyses.txt


mkdir Stats/moveset
echo Compiling Moveset Analyses...
for tier in "balancedhackmons" "cap" "dwou" "dwubers" "glitchmons" "hackmons" "lc" "nu" "ou" "oususpecttest" "ru" "ubers" "uu"
do
	python batchMovesetCounter.py $tier > Stats/moveset/$tier.txt
done

echo [B]Moveset Statistics[/B] > Moveset\ Statistics.txt
echo OU >> Moveset\ Statistics.txt
pastebinit Stats/moveset/ou.txt >> Moveset\ Statistics.txt
echo UU >> Moveset\ Statistics.txt
pastebinit Stats/moveset/uu.txt >> Moveset\ Statistics.txt
echo RU >> Moveset\ Statistics.txt
pastebinit Stats/moveset/ru.txt >> Moveset\ Statistics.txt
echo NU >> Moveset\ Statistics.txt
pastebinit Stats/moveset/nu.txt >> Moveset\ Statistics.txt
echo Ubers >> Moveset\ Statistics.txt
pastebinit Stats/moveset/ubers.txt >> Moveset\ Statistics.txt
echo LC >> Moveset\ Statistics.txt
pastebinit Stats/moveset/lc.txt >> Moveset\ Statistics.txt
echo DW OU >> Moveset\ Statistics.txt
pastebinit Stats/moveset/dwou.txt >> Moveset\ Statistics.txt
echo DW Ubers >> Moveset\ Statistics.txt
pastebinit Stats/moveset/dwubers.txt >> Moveset\ Statistics.txt
echo CAP >> Moveset\ Statistics.txt
pastebinit Stats/moveset/cap.txt >> Moveset\ Statistics.txt
echo Hackmons >> Moveset\ Statistics.txt
pastebinit Stats/moveset/hackmons.txt >> Moveset\ Statistics.txt
echo Balanced Hackmons >> Moveset\ Statistics.txt
pastebinit Stats/moveset/balancedhackmons.txt >> Moveset\ Statistics.txt
echo Glitchmons >> Moveset\ Statistics.txt
pastebinit Stats/moveset/glitchmons.txt >> Moveset\ Statistics.txt
echo OU Suspect Test >> Moveset\ Statistics.txt
pastebinit Stats/moveset/oususpecttest.txt >> Moveset\ Statistics.txt
