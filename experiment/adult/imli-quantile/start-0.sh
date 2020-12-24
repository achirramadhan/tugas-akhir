#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/adult/imli-quantile"

python $DIR_RUNNER/imli_runner_methodology_validation_quantile.py adult 0 1 3 5 6 7 8 13 >$DIR_RESULT/result-imli-quantile-adult-0.txt 2>&1
