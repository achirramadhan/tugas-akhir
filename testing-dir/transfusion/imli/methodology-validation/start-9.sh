#!/bin/bash
HOME="/root"
DIR_RUNNER="$HOME/skripsi/experiment/imli/testing-dir"
DIR_RESULT="$HOME/skripsi/experiment/imli/testing-dir/transfusion/imli/methodology-validation"
PATH="$HOME/skripsi/open-wbo:$PATH"
PATH="$HOME/skripsi/MaxHS/build/release/bin:$PATH"
echo $PATH

python $DIR_RUNNER/imli_runner_methodology_validation.py transfusion 9 >$DIR_RESULT/result-imli-transfusion-9.txt 2>&1
