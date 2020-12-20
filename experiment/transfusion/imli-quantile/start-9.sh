#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/transfusion/imli-quantile"

python $DIR_RUNNER/imli_runner_methodology_validation_quantile.py transfusion 9 >$DIR_RESULT/result-imli-quantile-transfusion-9.txt 2>&1
