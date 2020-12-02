#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/wdbc/mlic"

python $DIR_RUNNER/mlic_runner_methodology_validation.py wdbc 1 >$DIR_RESULT/result-mlic-wdbc-1.txt 2>&1
