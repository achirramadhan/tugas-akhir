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
    solver="/root/skripsi/open-wbo/open-wbo"
    solver_timeout=1000

    # Testing
    import time

    print("lamda, n_clause, rule_type, size, id_cv, training_time, accuracy")

    max_test_acc_holdout = 0
    chosen_mean_val_acc = 0
    chosen_model = None
    chosen_params = None
    chosen_training_time = 0
    for lamda in lambdas:
        for n_clause in n_clauses:
            for rule_type in rule_types:

                skf = StratifiedKFold(n_splits=k_cv, random_state=42, shuffle=True)
                id_cv = 0

                sum_val_acc_cv = 0
                max_val_acc_cv = 0
                best_model = None
                best_params = None
                sum_model_training_time = 0
                for train_id, val_id in skf.split(X_train_val, y_train_val):
                    N = train_id.shape[0]

                    real_size = [N]

                    from MLIC import MLIC
                    mlic = MLIC(
                        n_clauses=n_clause,
                        lamda=lamda,
                        rule_type=rule_type,
                        solver=solver,
                        solver_timeout=solver_timeout)

                    start_time = time.time()
                    mlic.fit(X_train_val[train_id], y_train_val[train_id])
                    end_time = time.time()
                    training_time = end_time - start_time

                    y_true = y_train_val[val_id]
                    y_pred = mlic.predict(X_train_val[val_id])

                    from sklearn.metrics import accuracy_score
                    accuracy = accuracy_score(y_true, y_pred)
                    sum_val_acc_cv += accuracy
                    sum_model_training_time += training_time
                    if accuracy > max_val_acc_cv:
                        max_val_acc_cv = accuracy
                        best_model = mlic
                        best_params = (lamda, n_clause, rule_type, real_size, id_cv)

                    print("%d,%d,%s,%s,%d,%f,%f" % (
                        lamda,
                        n_clause,
                        rule_type,
                        real_size,
                        id_cv,
                        training_time,
                        accuracy))

                    id_cv += 1

                mean_val_acc_cv = sum_val_acc_cv / k_cv
                mean_model_training_time = sum_model_training_time / k_cv

                y_pred_test = best_model.predict(X_test)
                y_true_test = y_test

                from sklearn.metrics import accuracy_score
                test_acc_holdout = accuracy_score(y_true_test, y_pred_test)

                print("---> Chosen: %s, (mean val acc cv) %f, (test acc holdout) %f, (mean training time) %f" % (
                    str(best_params),
                    mean_val_acc_cv,
                    test_acc_holdout,
                    mean_model_training_time))

                if (test_acc_holdout > max_test_acc_holdout) or \
                    ((test_acc_holdout == max_test_acc_holdout) and (mean_val_acc_cv > chosen_mean_val_acc)):
                    max_test_acc_holdout = test_acc_holdout
                    chosen_mean_val_acc = mean_val_acc_cv
                    chosen_model = best_model
                    chosen_params = best_params
                    chosen_training_time = mean_model_training_time

    print("------------------")
    print("HOLDOUT %d" % ID_HOLDOUT)
    print("size training + validation:", X_train_val.shape)
    print("size testing:", X_test.shape)
    print("max_test_acc_holdout: %f" % max_test_acc_holdout)
    print("chosen_params: %s" % [str(u) for u in chosen_params])
    print("chosen_mean_val_acc: %f" % chosen_mean_val_acc)
    print("chosen_training_time: %f" % chosen_training_time)
    print("chosen_model_rule:")
    print(chosen_model.get_rule())

if __name__=="__main__":
    run_imli(sys.argv[1], int(sys.argv[2]))
