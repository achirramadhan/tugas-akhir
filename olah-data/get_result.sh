#!/bin/bash

# t: size training
# t: size testing
# t: test_acc_holdout
# t: 
# t: best_val_accs
# t: best_mean_val_acc
# t: chosen_params
# t: 
# t: chosen_cv_training_time
# t: chosen_mean_cv_training_time
# t: retrain_training_time
# t: 
# t: best_model_rule_size (retrained with params)
# t: best_model_rule (retrained with params)
# t: 
# t: n_features (retrained with params)
# t: real_partition_size (retrained with params)
# t: 
# t: test_classification_report_holdout
# t: 
# t: train_val_classification_report_holdout


cat ../experiment/$2/$1/result-$1-$2-*.txt | grep "$3"