#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/wdbc/mlic-quantile"

python $DIR_RUNNER/mlic_runner_methodology_validation_quantile.py wdbc 5 >$DIR_RESULT/result-mlic-quantile-wdbc-5.txt 2>&1
