Smogon-Usage-Stats
==================

Scripts for compiling usage stats from Smogon's Pokemon Showdown server



Each month, Smogon's PS server logs millions of battles across dozens of metagames. These scripts read in those logs and distill them into usage statistics, from the simple counts used for tiering to detailed moveset and metagame statistics. The method for this boils down to the following:

1. Assume that logs are stored in the /logs/ folder (I'll be assuming a UNIX system) and that you've cloned this repo into the /Smogon-Usage-Stats/ folder. The /logs/ folder should be subdivided first by month, then by metagame, then by day. So Little Cup battles from June 3, 2013 will be found in: /logs/2013-06/lc/2013-06-03/

2. batchLogReader.py is written to loop over all PS logs stored in one of these subdirectories and gather any relevant information into intermediate files, which will be stored in the /Smogon-Usage-Stats/Raw/ folder. In olden days, back before PS' popularity was quite where it is now, these files were human-readible ASCII, with each line being a JSON-format string containing the relevant battle information. Nowadays, those files would be just too large (over 20GB in May 2013), so instead we use the lzma library to compress the data. Since batchLogReader.py is designed to process single log subfolders at a time, it can be run nightly, cutting down on the amount of processing that needs to be done at the end of the month.

3. At the end of the month, once all the logs are "read" by batchLogReader.py and processed into intermediate files, which are stored in /Smogon-Usage-Stats/Raw/, we run StatCounter.py, which reads in the intermediate file and does all the counting necessary to generate usage statistics, lead statistics and metagame analyses. These are generated into the /Smogon-Usage-Stats/Stats/ folder. StatCounter.py also generates additional moveset information, namely teammate data and the so-called "encounterMatrix" which is used to determine checks and counters.

4. Once StatCounter.py has run its course, batchMovesetCounter.py may be run to generate detailed moveset statistics for any Pokemon that appears on at least than 0.01% of teams. This script depends on StatCounter.py having already been run (otherwise, there will be missing files).



There are additional scripts as well, but their functions and usage should (hopefully) be documented in their respective files.

What follows is basic script usage, assuming everything is stored in the folders set out in (1). All commands assume that the user is in the /Smogon-Usage-Stats directory.

To process PS logs for a given tier (say Little Cup) for a given day (say 2013-06-03):

$python batchLogReader.py /logs/2013-06/lc/2013-06-03/ lc

The first argument gives the location of the folder. The second gives the name of the metagame.


Now let's assume all the logs are processed and their intermediate files stored in /Smogon-Usage/Stats/Raw/. Then to generate all usage stats except for metagame analyses:

$python StatCounter.py lc

The first argument is the name of the tier. Note that StatCounter.py can also take a second argument, which gives the (Glicko2) rating cutoff for weighted stats. If no argument is given, the standard 1500 cutoff is assumed. If you want unweighted stats, use:

$python StatCounter.py lc 0

and if you want "1850" stats, use:

$python StatCounter.py lc 1850

Now if you want detailed moveset statistics, use the batchMovesetCounter.py script:

$python batchMovesetCounter.py lc > Stats/moveset/lc.txt

Note that the moveset stats are written to stdout, so you need to redirect the output to the file where you want the stats stored (make sure the Stats/moveset/ folder exists).

If you want moveset stats for a different cutoff besides the standard 1500, use the same syntax as before. For example, for 1850 moveset stats, use:

$python batchMovesetCounter.py lc 1850 > Stats/moveset/lc-1850.txt



That's all I can think of for now. I'll add more if I think of anything.
