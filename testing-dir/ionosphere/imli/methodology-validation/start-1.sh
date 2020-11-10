#!/bin/bash
HOME="/root"
DIR="$HOME/skripsi/experiment/imli/testing-dir/ionosphere/imli/methodology-validation"
PATH="$HOME/skripsi/open-wbo:$PATH"
PATH="$HOME/skripsi/MaxHS/build/release/bin:$PATH"
echo $PATH

python $DIR/imli_runner_methodology_validation.py ionosphere 1 >$DIR/result-imli-ionosphere-1.txt 2>&1
