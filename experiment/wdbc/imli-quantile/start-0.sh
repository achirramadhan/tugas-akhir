#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/wdbc/imli-quantile"

python $DIR_RUNNER/imli_runner_methodology_validation_quantile.py wdbc 0 >$DIR_RESULT/result-imli-quantile-wdbc-0.txt 2>&1
