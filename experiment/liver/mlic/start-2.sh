#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/liver/mlic"

python $DIR_RUNNER/mlic_runner_methodology_validation.py liver 2 >$DIR_RESULT/result-mlic-liver-2.txt 2>&1
