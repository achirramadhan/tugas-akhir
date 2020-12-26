#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/adult/mlic-quantile"

python $DIR_RUNNER/mlic_runner_methodology_validation_quantile.py adult 5 1 3 5 6 7 8 13 >$DIR_RESULT/result-mlic-quantile-adult-5.txt 2>&1
