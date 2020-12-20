#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/liver/imli-quantile"

python $DIR_RUNNER/imli_runner_methodology_validation_quantile.py liver 6 >$DIR_RESULT/result-imli-quantile-liver-6.txt 2>&1
