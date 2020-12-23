#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/liver/mlic-quantile"

python $DIR_RUNNER/mlic_runner_methodology_validation_quantile.py liver 5 >$DIR_RESULT/result-mlic-quantile-liver-5.txt 2>&1
