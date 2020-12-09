#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/adult/mlic"

python $DIR_RUNNER/mlic_runner_methodology_validation.py adult 3 1 3 5 6 7 8 13 >$DIR_RESULT/result-mlic-adult-3.txt 2>&1
