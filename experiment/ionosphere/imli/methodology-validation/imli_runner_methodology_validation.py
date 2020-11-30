import sys
sys.path.insert(1, '/root/skripsi/experiment/imli')

def run_imli(DATASET_NAME, ID_HOLDOUT):
    # Load Dataset
    import pandas as pd
    HOLDOUT_DIR = "/root/skripsi/experiment/imli/testing-dir/%s/holdout/" % DATASET_NAME
    df_train_val = pd.read_csv(HOLDOUT_DIR + ("%s-%d-train.csv" % (DATASET_NAME, ID_HOLDOUT))).sample(frac=1)
    df_test = pd.read_csv(HOLDOUT_DIR + ("%s-%d-test.csv" % (DATASET_NAME, ID_HOLDOUT))).sample(frac=1)

    import numpy as np

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
    solver="/root/skripsi/open-wbo/open-wbo"
    timeout=1000

    # Testing
    import time

    print("l: lamda, n_clause, rule_type, train_size, val_size, id_cv, real_partition_size, n_partitions, n_features, training_time, accuracy, rule_size, rule")

    best_mean_val_acc = 0
    chosen_val_accs = []
    chosen_params = {}
    chosen_training_time = []
    for lamda in lambdas:
        for n_clause in n_clauses:
            for rule_type in rule_types:
                for partition_size, is_floor in zip(partition_sizes, is_floors):

                    skf = StratifiedKFold(n_splits=k_cv, shuffle=True)
                    id_cv = 0

                    val_accs_cv = []
                    model_training_times = []
                    n_partitions_s = []
                    for train_id, val_id in skf.split(X_train_val, y_train_val):
                        N = train_id.shape[0]

                        if is_floor: # floor, minimum partition_size
                            n_partitions = N // partition_size
                        else: # ceiling, maximum partition_size
                            n_partitions = (N + partition_size - 1) // partition_size
                        
                        n_partitions_s.append(n_partitions)

                        train_size = N
                        val_size = val_id.shape[0]
                        real_partition_size = [N // n_partitions, (N + n_partitions - 1) // n_partitions]

                        from IMLI import IMLI
                        imli = IMLI(
                            n_clauses=n_clause,
                            lamda=lamda,
                            rule_type=rule_type,
                            solver=solver,
                            n_partitions=n_partitions,
                            timeout=timeout)

                        start_time = time.time()
                        imli.fit(X_train_val[train_id], y_train_val[train_id])
                        end_time = time.time()
                        training_time = end_time - start_time

                        y_true = y_train_val[val_id]
                        y_pred = imli.predict(X_train_val[val_id])

                        from sklearn.metrics import accuracy_score
                        accuracy = accuracy_score(y_true, y_pred)
                        val_accs_cv.append(accuracy)
                        model_training_times.append(training_time)
                        
                        # lamda, n_clause, rule_type, train_size, val_size, id_cv, real_partition_size, n_partitions, n_features, training_time, accuracy, rule_size, rule
                        
                        n_features = imli.n_features
                        rule = imli.get_rule()
                        rule_size = imli.get_rule_size()
                        print("l: %d,%d,%s,%d,%d,%d,%s,%d,%d,%f,%f,%d,%s" % (
                            lamda,
                            n_clause,
                            rule_type,
                            train_size,
                            val_size,
                            id_cv,
                            real_partition_size,
                            n_partitions,
                            n_features,
                            training_time,
                            accuracy,
                            rule_size,
                            rule
                        ))

                        id_cv += 1

                    mean_val_acc_cv = np.mean(val_accs_cv)
                    std_val_acc_cv = np.std(val_accs_cv)
                    mean_model_training_time = np.mean(model_training_times)
                    std_model_training_time = np.std(model_training_times)
                    
                    # n_partitions
                    (values,counts) = np.unique(n_partitions_s, return_counts=True)
                    n_partitions = values[counts.argmax()]
                    
                    params = {
                        'lamda': lamda,
                        'n_clause': n_clause,
                        'rule_type': rule_type,
                        'real_partition_size': real_partition_size,
                        'n_partitions': n_partitions
                    }

                    print("r: ---> Result: %s, (mean val acc cv) %f (std: %f), (mean training time) %f (std: %f)" % (
                        str(params),
                        mean_val_acc_cv,
                        std_val_acc_cv,
                        mean_model_training_time,
                        std_model_training_time
                    ))

                    if (mean_val_acc_cv > best_mean_val_acc):
                        best_mean_val_acc = mean_val_acc_cv
                        chosen_val_accs = val_accs_cv
                        chosen_params = params
                        chosen_training_time = model_training_times
    
    best_model = IMLI(
        n_clauses=chosen_params['n_clause'],
        lamda=chosen_params['lamda'],
        rule_type=chosen_params['rule_type'],
        solver=solver,
        n_partitions=chosen_params['n_partitions'],
        timeout=timeout)
    
    start_time = time.time()
    best_model.fit(X_train_val, y_train_val)
    end_time = time.time()
    retrain_training_time = end_time - start_time
    
    y_pred_test = best_model.predict(X_test)
    y_true_test = y_test

    from sklearn.metrics import accuracy_score
    test_acc_holdout = accuracy_score(y_true_test, y_pred_test)

    # lamda, n_clause, rule_type, train_size, val_size, id_cv, real_partition_size, n_partitions, n_features, training_time, accuracy, rule_size, rule
    
    N = X_train_val.shape[0]
    n_partitions=chosen_params['n_partitions']
    real_partition_size = [N // n_partitions, (N + n_partitions - 1) // n_partitions]
        
    print("t: ------------------")
    print("t: HOLDOUT %d" % ID_HOLDOUT)
    print("t: size training:", X_train_val.shape)
    print("t: size testing:", X_test.shape)
    print("t: test_acc_holdout: %f" % test_acc_holdout)
    print("t: ")
    print("t: best_val_accs: %s", chosen_val_accs)
    print("t: best_mean_val_acc: %f (std: %f)" % (np.mean(chosen_val_accs), np.std(chosen_val_accs)))
    print("t: chosen_params: {}".format(chosen_params))
    print("t: ")
    print("t: chosen_cv_training_time: %s" % chosen_training_time)
    print("t: chosen_mean_cv_training_time: %f (std: %f)" % (np.mean(chosen_training_time), np.std(chosen_training_time)))
    print("t: retrain_training_time: %f" % retrain_training_time)
    print("t: ")
    print("t: best_model_rule_size (retrained with params): %d" % best_model.get_rule_size())
    print("t: best_model_rule (retrained with params):")
    print("t: " + best_model.get_rule())
    print("t: ")
    print("t: n_features (retrained with params): %d" % best_model.n_features)
    print("t: real_partition_size (retrained with params): %s" % real_partition_size)

if __name__=="__main__":
    run_imli(sys.argv[1], int(sys.argv[2]))
