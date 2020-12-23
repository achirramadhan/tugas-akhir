#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/ionosphere/imli-quantile"

python $DIR_RUNNER/imli_runner_methodology_validation_quantile.py ionosphere 2 >$DIR_RESULT/result-imli-quantile-ionosphere-2.txt 2>&1
