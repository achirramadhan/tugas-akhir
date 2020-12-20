#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/imli/experiment"
DIR_RESULT="$HOME/skripsi/imli/experiment/liver/imli"

python $DIR_RUNNER/imli_runner_methodology_validation.py liver 4 >$DIR_RESULT/result-imli-liver-4.txt 2>&1
