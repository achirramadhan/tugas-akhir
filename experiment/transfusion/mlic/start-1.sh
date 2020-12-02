#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/transfusion/mlic"

python $DIR_RUNNER/mlic_runner_methodology_validation.py transfusion 1 >$DIR_RESULT/result-mlic-transfusion-1.txt 2>&1
