#!/bin/bash

function process {
	tier=monotype
	tag=$1

	echo "Processing "$tag >> log.log

	pypy StatCounter.py $tier 1630 $tag &&
	pypy batchMovesetCounter.py $tier 1630 $tag > Stats/moveset/$tier-$tag-1630.txt
#	pypy MegaCounter.py Stats/chaos/$tier-$tag-1630.json > Stats/mega/$tier-$tag-1630.txt


	pypy StatCounter.py $tier 1760 $tag &&
	pypy batchMovesetCounter.py $tier 1760 $tag > Stats/moveset/$tier-$tag-1760.txt
#	pypy MegaCounter.py Stats/chaos/$tier-$tag-1760.json > Stats/mega/$tier-$tag-1760.txt

	pypy StatCounter.py $tier 0 $tag &&
	pypy batchMovesetCounter.py $tier 0 $tag > Stats/moveset/$tier-$tag-0.txt
#	pypy MegaCounter.py Stats/chaos/$tier-$tag-0.json > Stats/mega/$tier-$tag-0.txt


	pypy StatCounter.py $tier 1500 $tag &&
	pypy batchMovesetCounter.py $tier 1500 $tag > Stats/moveset/$tier-$tag-1500.txt
#	pypy MegaCounter.py Stats/chaos/$tier-$tag-1500.json > Stats/mega/$tier-$tag-1500.txt
	
	
	
}
export -f process

parallel -j 3 process ::: mononormal monofighting monoflying monopoison monoground monorock monobug monoghost monosteel monofire monowater monograss monoelectric monopsychic monoice monodragon monodark monofairy
mkdir Stats/monotype
mv Stats/monotype-mono* Stats/monotype/.
for d in chaos leads metagame moveset
do
	mkdir Stats/monotype/$d
	mv Stats/$d/monotype-mono* Stats/monotype/$d/.
done
