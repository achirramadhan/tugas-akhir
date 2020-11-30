#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/ionosphere/imli"

python $DIR_RUNNER/imli_runner_methodology_validation.py ionosphere 7 >$DIR_RESULT/result-imli-ionosphere-7.txt 2>&1
