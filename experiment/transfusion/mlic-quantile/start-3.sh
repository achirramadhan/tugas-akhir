#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/transfusion/mlic-quantile"

python $DIR_RUNNER/mlic_runner_methodology_validation_quantile.py transfusion 3 >$DIR_RESULT/result-mlic-quantile-transfusion-3.txt 2>&1
