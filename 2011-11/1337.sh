mkdir Stats/1337
python ../StatCounter1337OnCrack.py "Raw/Standard OU Rated.txt" ratings/OU.txt > "Stats/1337/Standard OU Rated.txt"
python ../StatCounter1337OnCrack.py "Raw/Standard UU Rated.txt" ratings/UU.txt > "Stats/1337/Standard UU Rated.txt"
python ../StatCounter1337OnCrack.py "Raw/Standard RU Rated.txt" ratings/RU.txt > "Stats/1337/Standard RU Rated.txt"
python ../StatCounter1337OnCrack.py "Raw/Standard NU Rated.txt" ratings/NU.txt > "Stats/1337/Standard NU Rated.txt"
python ../StatCounter1337OnCrack.py "Raw/Standard Ubers Rated.txt" ratings/Ubers.txt > "Stats/1337/Standard Ubers Rated.txt"
python ../StatCounter1337OnCrack.py "Raw/Standard LC Rated.txt" ratings/LC.txt > "Stats/1337/Standard LC Rated.txt"

echo [b]1337 stats![/b] > 1337\ Stats.txt
echo This data only takes into account teams whose user has a current rating--as of 11/1*--of 1337 or higher. In tiers where there were not enough players with a rating that high, I lowered the cutoff as specified. >> 1337\ Stats.txt
echo >> 1337\ Stats.txt
echo *Once the server is back up, I will use ratings generated as of 12/1. >> 1337\ Stats.txt
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
