#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/adult/imli"

python $DIR_RUNNER/imli_runner_methodology_validation.py adult 8 1 3 5 6 7 8 13 >$DIR_RESULT/result-imli-adult-8.txt 2>&1
