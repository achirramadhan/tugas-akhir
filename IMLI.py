import numpy as np
import Orange
import os
import random

class Feature:
    def __init__(self, name, feature_type, thresholds=None, categories=None):
        self.name = name
        self.feature_type = feature_type
        self.thresholds = thresholds
        self.categories = categories

    def __str__(self):
        return self.name
    
class CategoricalFeature(Feature):
    def __init__(self, orig_feature_id, sign, category):
        name = "X{} {} {}".format(orig_feature_id, sign, category)
        super().__init__(name, "categorical")
        self.orig_feature_id = orig_feature_id
        self.op = sign
        self.category = category
        
    def negation(self):
        negated_op = "==" if self.op == "!=" else "!="
        return CategoricalFeature(self.orig_feature_id, negated_op, self.category)
    
class BinaryFeature(Feature):
    def __init__(self, is_negated, orig_feature_id):
        if is_negated:
            name = "(NOT X%d)" % orig_feature_id
        else:
            name = "X%d" % orig_feature_id
                
        super().__init__(name, "binary")
        self.is_negated = is_negated # True or False
        self.orig_feature_id = orig_feature_id
        
    def negation(self):
        return BinaryFeature(not self.is_negated, self.orig_feature_id)
        
class DiscretizedFeature(Feature):
    def __init__(self, source_feature, orig_feature_id, sign, threshold):
        name = "X%d %s %f" % (orig_feature_id, sign, threshold)
        
        super().__init__(name, "discretized")
        self.source_feature = source_feature
        self.orig_feature_id = orig_feature_id
        self.op = sign # >= or <
        self.tval = threshold
        
    def siblings(self, other):
        if not isinstance(other, DiscretizedFeature):
            return False
        if self.source_feature != other.source_feature:
            return False
        
        return self.op == other.op
    
    def negation(self):
        negated_op = ">=" if self.op == "<" else "<"
        return DiscretizedFeature(self.source_feature, self.orig_feature_id, negated_op, self.tval)

class IMLI:    
    def __init__(self, n_clauses=3, lamda=3, solver="open-wbo", n_partitions=1, rule_type="CNF", verbose=0, timeout=3600):
        self.n_clauses = n_clauses
        self.lamda = lamda
        self.solver = solver
        self.n_partitions = n_partitions
        self.rule_type = rule_type
        self.verbose = verbose
        self.timeout = timeout
        
        self.B = []
        self.eta = []
        self.n_features = 0
        self.new_features = []
        self.raw_features = []
            
    def _get_id_maxsat_B(self, l, j):
        return l * self.n_features + j + 1
    
    def _get_id_maxsat_eta(self, q):
        return self.n_clauses * self.n_features + q + 1
    
    def _generate_B_eta(self, assignment, n_samples):
        idx = 0
        B = np.zeros((self.n_clauses, self.n_features))
        for l in range(self.n_clauses):
            for j in range(self.n_features):
                B[l][j] = 1 if assignment[idx] > 0 else 0
                idx += 1
        
        eta = np.zeros((n_samples,))
        for q in range(n_samples):
            eta[q] = 1 if assignment[idx] > 0 else 0
            idx += 1
        
        return B, eta        
    
    def _maxsat_solve(self, X, y):
        n_samples = y.shape[0]

        random_file_index = random.randint(0, 1000000000000000000)
        qname = "query_%d_%d_%d_%d_%s.wcnf" % (random_file_index, self.n_clauses, self.lamda, self.n_partitions, self.rule_type)
        with open(qname, "w") as f:            
            # define parameters            
            unique, counts = np.unique(y, return_counts = True)
            num_occurence = dict(zip(unique, counts))
            
            nbvar = self.n_features * self.n_clauses + n_samples + num_occurence[0] * self.n_clauses
            nbclauses = self.n_features * self.n_clauses \
                        + n_samples \
                        + num_occurence[0] * (1 + self.n_clauses * (self.n_features // 2)) \
                        + num_occurence[1] * self.n_clauses
            
            top = self.n_features * self.n_clauses + n_samples * self.lamda + 1
            
            line = "p wcnf %d %d %d\r\n" % (nbvar, nbclauses, top)
            f.write(line)
            
            # Constraints
            # We change the indexing system from the paper to 0-based indexing
            # Here, we encode each propositional to maxsat index as follows:
            # 1. B_l_j = variable index (l * n_features + j + 1),
            # 2. eta_q = variable index (n_clauses * n_features + q + 1),
            # 3. z_i_j = the rest, the numbering isn't important since
            #            each of them is only used once
            
            # first constraint
            idx = 1
            for l in range(self.n_clauses):
                for j in range(self.n_features):
                    v = -idx
                    if self.B[l][j] == 1:
                        v = idx

                    line = "%d %d 0\r\n" % (1, v)
                    f.write(line)
                    idx += 1 # idx = l * n_features + j + 1
            
            # second constraint
            for q in range(n_samples):
                line = "%d %d 0\r\n" % (self.lamda, -(idx))
                f.write(line)
                idx += 1 # idx = (n_clauses * n_features) + q + 1
            
            # third constraint
            for q in range(n_samples):
                id_eta_q = self._get_id_maxsat_eta(q)
                X_q = X[q]
                on_features = [i for i in range(X_q.shape[0]) if X_q[i] == 1]
                if y[q] == 0:
                    id_z_q_1 = idx
                    
                    # D_q_0
                    clause = [id_eta_q] + [id_z_q_1 + l for l in range(self.n_clauses)]
                    line = str(top) + ' ' + ' '.join(str(u) for u in clause) + ' 0\r\n'
                    f.write(line)
                    
                    # D_q_l
                    for l in range(self.n_clauses):
                        id_z_q_l = id_z_q_1 + l
                        for u in on_features:
                            clause = [-id_z_q_l, -self._get_id_maxsat_B(l, u)]
                            line = str(top) + ' ' + ' '.join(str(u) for u in clause) + ' 0\r\n'
                            f.write(line)
                        
                    idx += self.n_clauses
                        
                elif y[q] == 1:
                    for l in range(self.n_clauses):
                        clause = [id_eta_q] + [l * self.n_features + u + 1 for u in on_features]
                        line = str(top) + ' ' + ' '.join(str(u) for u in clause) + ' 0\r\n'
                        f.write(line)
                    
        # maxSAT
        rname = "result_%d_%d_%d_%d_%s.txt" % (random_file_index, self.n_clauses, self.lamda, self.n_partitions, self.rule_type)

        if self.verbose == 1:
            print("MAXSAT SOLVER PROCESSING")
            
        solver_timeout = (self.timeout + self.n_partitions - 1) // self.n_partitions
        if solver_timeout < 1:
            solver_timeout = 1
        os.system("%s -cpu-lim=%d ./%s > %s" % (self.solver, solver_timeout, qname, rname))
        
        if self.verbose == 1:
            print("MAXSAT SOLVER DONE")
        
        # get result
        assignment_found = False
        with open(rname, "r") as f:
            lines = f.readlines()
            for line in lines:
                if not line or line[0] == 'c':
                    continue
                elif line[0] == 'v':
                    assignment = [int(u) for u in line.strip().split()[1:] ]
                    if assignment != []:
                        assignment_found = True
                    self.B, self.eta = self._generate_B_eta(assignment, n_samples)
        
        if not assignment_found:
            raise Exception("%s fail to return assignment." % self.solver)
        
        os.remove(rname)
        os.remove(qname)

    def _remove_redundant_literals(self, B):
        new_features = self.new_features
        n_features = self.n_features

        for l in range(self.n_clauses):
            id_online_features = [j for j in range(self.n_features) if B[l][j] == 1]
            for i in id_online_features:
                if not isinstance(new_features[i], DiscretizedFeature):
                    continue

                for j in id_online_features:
                    if not isinstance(new_features[j], DiscretizedFeature) \
                        or not new_features[i].siblings(new_features[j]) \
                        or new_features[i].tval >= new_features[j].tval:
                        continue

                    if new_features[i].op == new_features[j].op == ">=":
                        B[l][j] = 0
                    else:
                        B[l][i] = 0
                    
                    if self.verbose == 1:
                        print("Redundant %d (%d) %s (%d) %s" % (l, i, new_features[i], j, new_features[j]))

        return B

    def _train(self, X, y):
        all_data = np.hstack([X, np.expand_dims(y, axis=1)])
        data = [
            all_data[all_data[:, -1] == 0],
            all_data[all_data[:, -1] == 1]
        ]

        rng = np.random.default_rng()
        for i in range(2):
            rng.shuffle(data[i])

        n = [data[0].shape[0], data[1].shape[0]]
        n_trained = [0, 0]

        # initialization of B
        self.B, self.eta = self._generate_B_eta(
            assignment=np.zeros(self.n_clauses * self.n_features),
            n_samples=0)

        p = self.n_partitions
        for i in range(p):
            if self.verbose == 1:
                print("ITERASI %d" % (i + 1))
            n_to_train = [0, 0]
            for j in range(2):
                n_to_train[j] = (n[j] // p) + (1 if i < n[j] % p else 0)
            
            data_to_maxsat = np.vstack([
                data[j][n_trained[j] : n_trained[j] + n_to_train[j]]
                    for j in range(2)
                ])

            rng.shuffle(data_to_maxsat)
            self._maxsat_solve(data_to_maxsat[:, :-1], data_to_maxsat[:, -1])

            for j in range(2):
                n_trained[j] += n_to_train[j]

            self.B = self._remove_redundant_literals(self.B)

            if self.verbose == 1:
                print(self.get_rule())
                print("------------------------------")

    def _is_binary_array(self, x):
        is_binary = True
        for u in x:
            if u != 0 and u != 1:
                is_binary = False
                break

        return is_binary
    
    def _append_X(self, feature_type, new_X, X, id_col, cur_feature, new_features=[], thresholds=None, categories=None):
        """
        Process raw features to new features, make sure every feature has its negation
        """
        if feature_type == "continuous":
            for sign in (">=", "<"):
                for point in thresholds:
                    if sign == ">=":
                        new_col = (np.expand_dims(X[:, id_col], axis=1) >= point).astype(np.int)
                    elif sign == "<":
                        new_col = (np.expand_dims(X[:, id_col], axis=1) < point).astype(np.int)
                    
                    new_X = np.append(new_X, new_col, axis=1)
                    new_features.append(DiscretizedFeature(
                            source_feature=cur_feature,
                            orig_feature_id=id_col,
                            sign=sign,
                            threshold=point
                            ))
                        
        elif feature_type == "binary":
            new_col = np.expand_dims(X[:, id_col], axis=1)
        
            new_X = np.append(new_X, new_col, axis=1)
            new_features.append(BinaryFeature(
                    is_negated=False,
                    orig_feature_id=id_col
                ))

            new_X = np.append(new_X, 1 - new_col, axis=1)
            new_features.append(BinaryFeature(
                    is_negated=True,
                    orig_feature_id=id_col
                ))
            
        elif feature_type == "categorical":
            for sign in ("==", "!="):
                for category in categories:
                    if sign == "==":
                        new_col = (np.expand_dims(X[:, id_col], axis=1) == category).astype(np.int)
                    elif sign == "!=":
                        new_col = (np.expand_dims(X[:, id_col], axis=1) != category).astype(np.int)
                    
                    new_X = np.append(new_X, new_col, axis=1)
                    new_features.append(CategoricalFeature(
                            orig_feature_id=id_col,
                            sign=sign,
                            category=category
                            ))
                
        else:
            raise Exception("Make sure your training and test set only contains binary and continuous values.")
        
        return new_X
    
    def generate_features(self, X, y, categorical_features_id=[], discretizer="entropy", n_thresholds=9):
        """
        Generate the dataset features to be used in this model
        Category feature must be represented as numbers
        categorical_features_id use 0-based indexing
        
        Return features: type and its thresholds/categories
        """
        raw_features = []
        
        if discretizer == "entropy":
            disc = Orange.preprocess.discretize.EntropyMDL()
            domain = Orange.data.Domain.from_numpy(X, y)
            orange_table = Orange.data.Table.from_numpy(domain, X, y)
            attrs = orange_table.domain.attributes
        
        for i in range(X.shape[1]):
            unique_vals = np.unique(X[:, i])
            if unique_vals.shape[0] < 2:
                # throw the feature by take is as a categorical feature with 0 category
                cur_feature = Feature(name="X%d" % i, feature_type="raw_categorical", categories=[])
            elif i in categorical_features_id:
                categories = np.unique(X[:, i])
                cur_feature = Feature(name="X%d" % i, feature_type="raw_categorical", categories=categories)
            elif self._is_binary_array(X[:, i]):
                cur_feature = Feature(name="X%d" % i, feature_type="raw_binary")
            else:
                if discretizer == "entropy":
                    attr = attrs[i]
                    disc_attr = disc(orange_table, attr)
                    thresholds = disc_attr.compute_value.points
                elif discretizer == "quantile":
                    if unique_vals.shape[0] <= n_thresholds + 1:
                        # exclude minimum since we use < and >=
                        thresholds = np.sort(unique_vals)[1:]
                    else:
                        quantile_thresholds = np.linspace(1./(n_thresholds + 1.), n_thresholds/(n_thresholds + 1.), n_thresholds)
                        thresholds = np.unique(np.quantile(X[:, i], quantile_thresholds))
                else:
                    assert False, 'Available discretizers are "entropy" and "quantile"'
                    
                cur_feature = Feature(name="X%d" % i, feature_type="raw_continuous", thresholds=thresholds)
               
            raw_features.append(cur_feature)

        assert self._is_binary_array(y), "Labels must be a 1D-binary array with 0/1 values."

        return raw_features
    
    def _preprocess(self, X):
        assert X.shape[1] == len(self.raw_features), "Data columns and number of features does not match"
        
        new_X = np.zeros((X.shape[0], 0))
        new_features = []
        for i, feature in enumerate(self.raw_features):
            if feature.feature_type == "raw_binary":
                new_X = self._append_X("binary", new_X, X, i, feature, new_features)
            elif feature.feature_type == "raw_continuous":
                new_X = self._append_X("continuous", new_X, X, i, feature, new_features, thresholds=feature.thresholds)
            elif feature.feature_type == "raw_categorical":
                new_X = self._append_X("categorical", new_X, X, i, feature, new_features, categories=feature.categories)
            else:
                assert False, 'feature type must be raw_binary, raw_continuous, or raw_categorical'
                
        return new_X, new_features
    
    def fit(self, X, y, raw_features):
        """
        Parameters
        ----------
        X : 2D-array of shape (n_samples, n_features)
            Training data
        
        y : 1D-array of shape (n_samples,) with values 0/1
            Target class
        """
        assert self._is_binary_array(y), "y must have values 0/1."
        
        self.raw_features = raw_features
        X, new_features = self._preprocess(X)
        n_features = X.shape[1]
        self.n_features = n_features
        self.new_features = new_features

        if self.rule_type == "CNF":
            self._train(X, y)
        elif self.rule_type == "DNF":
            self._train(X, 1 - y)
        else:
            raise Exception('Rule type must be "CNF" or "DNF".')
    
    def predict(self, X):
        """
        Parameters
        ----------
        X : 2D-array of shape (n_samples, n_features)
            Samples.
        
        Returns
        -------
        C : 1D-array of shape (n_samples,)
            Returns predicted values.
        """
        
        X, _ = self._preprocess(X)
        preds = np.matmul(X, self.B.T).prod(axis=1)
        
        preds = (preds > 0).astype(np.int)
        
        if self.rule_type == "CNF":
            return preds
        elif self.rule_type == "DNF":
            return 1 - preds
        else:
            raise Exception('Rule type must be "CNF" or "DNF".')
    
    def _clause_to_str(self, clause):
        n_features = self.n_features
        new_features = self.new_features
        
        if self.rule_type == "CNF":
            literals = [new_features[j].name for j in range(n_features) if clause[j] == 1]
            return "[" + " OR ".join(literals) + "]"
        elif self.rule_type == "DNF":
            literals = [new_features[j].negation().name for j in range(n_features) if clause[j] == 1]
            return "[" + " AND ".join(literals) + "]"
                 
    def get_rule(self):
        # unique_clauses = np.unique(self.B, axis = 0)
        unique_clauses = self.B
        rules_array = [self._clause_to_str(clause) for clause in unique_clauses if clause.size > 0]
        
        if self.rule_type == "CNF":
            rule = " AND ".join(rules_array)
        elif self.rule_type == "DNF":
            rule = " OR ".join(rules_array)
        
        return rule
    
    def get_rule_size(self):
        return np.sum(self.B)
