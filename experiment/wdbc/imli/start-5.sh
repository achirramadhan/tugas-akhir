#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/wdbc/imli"

python $DIR_RUNNER/imli_runner_methodology_validation.py wdbc 5 >$DIR_RESULT/result-imli-wdbc-5.txt 2>&1
