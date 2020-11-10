#!/bin/bash
HOME="/root"
DIR="$HOME/skripsi/experiment/imli/testing-dir/ionosphere/mlic/methodology-validation"
PATH="$HOME/skripsi/open-wbo:$PATH"
PATH="$HOME/skripsi/MaxHS/build/release/bin:$PATH"
echo $PATH

python $DIR/mlic_runner_methodology_validation.py ionosphere 6 >$DIR/result-mlic-ionosphere-6.txt 2>&1
