#!/bin/bash
HOME="/root"
DIR="$HOME/skripsi/experiment/imli/testing-dir/ionosphere/mlic/methodology-paper"
PATH="$HOME/skripsi/open-wbo:$PATH"
PATH="$HOME/skripsi/MaxHS/build/release/bin:$PATH"
echo $PATH

python $DIR/mlic_runner_methodology_paper.py ionosphere 9 >$DIR/result-mlic-ionosphere-9.txt 2>&1
