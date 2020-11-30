#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/ionosphere/mlic"

python $DIR_RUNNER/mlic_runner_methodology_validation.py ionosphere 4 >$DIR_RESULT/result-mlic-ionosphere-4.txt 2>&1
