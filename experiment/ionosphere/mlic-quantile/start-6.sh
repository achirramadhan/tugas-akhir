#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/ionosphere/mlic-quantile"

python $DIR_RUNNER/mlic_runner_methodology_validation_quantile.py ionosphere 6 >$DIR_RESULT/result-mlic-quantile-ionosphere-6.txt 2>&1
