#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/transfusion/imli"

python $DIR_RUNNER/imli_runner_methodology_validation.py transfusion 7 >$DIR_RESULT/result-imli-transfusion-7.txt 2>&1
