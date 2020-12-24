import sys
sys.path.insert(1, '/root/skripsi/imli')

def run_imli(DATASET_NAME, ID_HOLDOUT, CATEGORICAL_FEATURES):
    # Load Dataset
    import pandas as pd
    HOLDOUT_DIR = "/root/skripsi/imli/experiment/%s/holdout/" % DATASET_NAME
    df_total = pd.read_csv(HOLDOUT_DIR + ("%s.csv" % DATASET_NAME))
    df_train_val = pd.read_csv(HOLDOUT_DIR + ("%s-%d-train.csv" % (DATASET_NAME, ID_HOLDOUT)))
    df_test = pd.read_csv(HOLDOUT_DIR + ("%s-%d-test.csv" % (DATASET_NAME, ID_HOLDOUT)))

    import numpy as np
    
    df_total_np = df_total.values
    X_total = df_total_np[:, :-1]
    y_total = df_total_np[:, -1]

    df_train_val_np = df_train_val.values
    X_train_val = df_train_val_np[:, :-1]
    y_train_val = df_train_val_np[:, -1]

    df_test_np = df_test.values
    X_test = df_test_np[:, :-1]
    y_test = df_test_np[:, -1]

    # Parameters
    from sklearn.model_selection import StratifiedKFold
    k_cv = 10
    lambdas = [5, 10]
    n_clauses = [1, 2, 3]
    rule_types = ["CNF", "DNF"]
    partition_sizes = [8, 16, 32, 64, 128]
    is_floors = [True, True, True, True, True]
    solver="/root/open-wbo/open-wbo"
    timeout=1000
    
    from IMLI import IMLI
    features = IMLI().generate_features(
        X_total,
        y_total,
        categorical_features_id=[int(u) for u in CATEGORICAL_FEATURES],
        discretizer="quantile",
        n_thresholds=9
    )

    # Testing
    import time

    print("l: lamda, n_clause, rule_type, id_cv, train_size, val_size, n_partitions, real_partition_size, n_features, training_time, val_accuracy, rule_size, rule, classification_report_train, classification_report_val")
    
    best_mean_val_acc = 0 # to choose hyperparameter (lamda, n_clause, rule_type)
    chosen_val_accs = [] # list of cv val accs from chosen hyperparameter
    chosen_params = {} # chosen hyperparameter
    chosen_training_times = [] # list of training time from chosen hyperparameter
    
    # finding best hyperparameter
    for lamda in lambdas:
        for n_clause in n_clauses:
            for rule_type in rule_types:
                for partition_size, is_floor in zip(partition_sizes, is_floors):
                    
                    skf = StratifiedKFold(n_splits=k_cv, shuffle=True, random_state=42)
                    id_cv = 0
                    
                    val_accs = []
                    training_times = []
                    n_partitions_s = []
                    
                    # cross validation start
                    for train_id, val_id in skf.split(X_train_val, y_train_val):
                        N = train_id.shape[0]
                        
                        if is_floor: # partition_size is the minimum allowed partition_size
                            n_partitions = N // partition_size
                        else:
                            n_partitions = (N + partition_size - 1) // partition_size
                            
                        n_partitions_s.append(n_partitions)
                        
                        train_size = N
                        val_size = val_id.shape[0]
                        
                        real_partition_size = [N // n_partitions, (N + n_partitions - 1) // n_partitions]
                        
                        imli = IMLI(
                            n_clauses=n_clause,
                            lamda=lamda,
                            rule_type=rule_type,
                            solver=solver,
                            n_partitions=n_partitions,
                            timeout=timeout)

                        start_time = time.time()
                        imli.fit(X_train_val[train_id], y_train_val[train_id], features)
                        end_time = time.time()
                        training_time = end_time - start_time
                        
                        training_times.append(training_time)
                        
                        # report validation data
                        y_true = y_train_val[val_id]
                        y_pred = imli.predict(X_train_val[val_id])

                        from sklearn.metrics import accuracy_score, classification_report
                        accuracy = accuracy_score(y_true, y_pred)
                        val_accs.append(accuracy)
                        
                        classification_report_val = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
                        
                        # report training data
                        y_true_train = y_train_val[train_id]
                        y_pred_train = imli.predict(X_train_val[train_id])
                        
                        classification_report_train = classification_report(y_true_train, y_pred_train, output_dict=True, zero_division=0)
                        
                        n_features = imli.n_features
                        rule = imli.get_rule()
                        rule_size = imli.get_rule_size()
                        
                        # lamda, n_clause, rule_type, id_cv, train_size, val_size, n_partitions, real_partition_size, n_features, training_time, val_accuracy, rule_size, rule, classification_report_train, classification_report_val
                        
                        print("l: %d,%d,%s,%d,%d,%d,%d,%s,%d,%f,%f,%d,%s,%s,%s" % (
                            lamda,
                            n_clause,
                            rule_type,
                            id_cv,
                            train_size,
                            val_size,
                            n_partitions,
                            str(real_partition_size).replace(',', ';'),
                            n_features,
                            training_time,
                            accuracy,
                            rule_size,
                            rule,
                            str(classification_report_train).replace(',', ';'),
                            str(classification_report_val).replace(',', ';')
                        ))
                        
                        id_cv += 1
                        
                    # cross validation done
                    mean_val_acc_cv = np.mean(val_accs)
                    std_val_acc_cv = np.std(val_accs)
                    mean_training_time = np.mean(training_times)
                    std_training_time = np.std(training_times)
                    
                    # n_partitions
                    (values, counts) = np.unique(n_partitions_s, return_counts=True)
                    n_partitions = values[counts.argmax()]
                    
                    params = {
                        'lamda': lamda,
                        'n_clause': n_clause,
                        'rule_type': rule_type,
                        'real_partition_size': real_partition_size,
                        'n_partitions': n_partitions
                    }
                    
                    print("r: ---> Params: %s, (mean val acc cv) %f (+- %f), (mean training time) %f (+- %f)" % (
                        str(params),
                        mean_val_acc_cv,
                        std_val_acc_cv,
                        mean_training_time,
                        std_training_time
                    ))

                    if (mean_val_acc_cv > best_mean_val_acc):
                        best_mean_val_acc = mean_val_acc_cv
                        chosen_val_accs = val_accs
                        chosen_params = params
                        chosen_training_time = training_times
                        
    # retrain using best hyperparameter
    best_model = IMLI(
        n_clauses=chosen_params['n_clause'],
        lamda=chosen_params['lamda'],
        rule_type=chosen_params['rule_type'],
        solver=solver,
        n_partitions=chosen_params['n_partitions'],
        timeout=timeout)
    
    start_time = time.time()
    best_model.fit(X_train_val, y_train_val, features)
    end_time = time.time()
    retrain_training_time = end_time - start_time
    
    # report test
    y_pred_test = best_model.predict(X_test)
    y_true_test = y_test

    from sklearn.metrics import accuracy_score, classification_report
    test_acc_holdout = accuracy_score(y_true_test, y_pred_test)
    test_classification_report_holdout = classification_report(y_true_test, y_pred_test, output_dict=True, zero_division=0)
    
    # report train val
    y_pred_train_val = best_model.predict(X_train_val)
    y_true_train_val = y_train_val
    train_val_classification_report_holdout = classification_report(y_true_train_val, y_pred_train_val, output_dict=True, zero_division=0)
    
    
    N = X_train_val.shape[0]
    n_partitions=chosen_params['n_partitions']
    real_partition_size = [N // n_partitions, (N + n_partitions - 1) // n_partitions]
        
    print("t: ------------------")
    print("t: HOLDOUT %d" % ID_HOLDOUT)
    print("t: size training:", X_train_val.shape)
    print("t: size testing:", X_test.shape)
    print("t: test_acc_holdout: %f" % test_acc_holdout)
    print("t: ")
    print("t: best_val_accs:", chosen_val_accs)
    print("t: best_mean_val_acc: %f (+- %f)" % (np.mean(chosen_val_accs), np.std(chosen_val_accs)))
    print("t: chosen_params: {}".format(chosen_params))
    print("t: ")
    print("t: chosen_cv_training_time: %s" % chosen_training_time)
    print("t: chosen_mean_cv_training_time: %f (+- %f)" % (np.mean(chosen_training_time), np.std(chosen_training_time)))
    print("t: retrain_training_time: %f" % retrain_training_time)
    print("t: ")
    print("t: best_model_rule_size (retrained with params): %d" % best_model.get_rule_size())
    print("t: best_model_rule (retrained with params):")
    print("t: " + best_model.get_rule())
    print("t: ")
    print("t: n_features (retrained with params): %d" % best_model.n_features)
    print("t: real_partition_size (retrained with params): %s" % real_partition_size)
    print("t: ")
    print("t: test_classification_report_holdout: %s" % str(test_classification_report_holdout).replace(',', ';'))
    print("t: ")
    print("t: train_val_classification_report_holdout: %s" % str(train_val_classification_report_holdout).replace(',', ';'))

if __name__=="__main__":
    run_imli(sys.argv[1], int(sys.argv[2]), list(sys.argv[3:]))
