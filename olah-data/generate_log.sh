#!/bin/bash

for I in 0 1 2 3 4 5 6 7 8 9
do
	cat ../experiment/$1/$2/result-$2-$1-$I.txt | grep l: | cut -c4- > $1/$2/log-$2-$I.csv
done

