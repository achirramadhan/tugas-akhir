#!/bin/bash
HOME="/root"
DIR="$HOME/skripsi/experiment/imli/testing-dir/ionosphere/imli/methodology-paper"
PATH="$HOME/skripsi/open-wbo:$PATH"
PATH="$HOME/skripsi/MaxHS/build/release/bin:$PATH"
echo $PATH

python $DIR/imli_runner_methodology_paper.py ionosphere 4 >$DIR/result-imli-ionosphere-4.txt 2>&1
