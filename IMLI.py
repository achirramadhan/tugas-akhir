import numpy as np
import Orange
import os
import random

class Feature:
    def __init__(self, name, feature_type, thresholds=None):
        self.name = name
        self.feature_type = feature_type
        self.thresholds = thresholds
        
class DiscretizedFeature(Feature):
    def __init__(self, name, source_feature, sign, threshold):
        super().__init__(name, "binary")
        self.source_feature = source_feature
        self.op = sign
        self.tval = threshold
        
    def siblings(self, other):
        if not isinstance(other, DiscretizedFeature):
            return False
        if self.source_feature != other.source_feature:
            return False
        
        return self.op == other.op

class IMLI:    
    def __init__(self, n_clauses=3, lamda=3, solver="open-wbo"):
        self.n_clauses = n_clauses
        self.lamda = lamda
        self.solver = solver
        
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
        
        random_file_index = random.randint(0, 1000000)
        qname = "query_%d.wcnf" % random_file_index
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
                    line = "%d %d 0\r\n" % (1, -(idx))
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
        rname = "result_%d.txt" % random_file_index

        print("MAXSAT SOLVER PROCESSING")
        os.system("%s ./%s > %s" % (self.solver, qname, rname))
        print("MAXSAT SOLVER DONE")
        
        # get result
        with open(rname, "r") as f:
            lines = f.readlines()
            for line in lines:
                if not line or line[0] == 'c':
                    continue
                elif line[0] == 'v':
                    assignment = [int(u) for u in line.split(' ')[1:-1] ]
                    self.B, self.eta = self._generate_B_eta(assignment, n_samples)
        
        os.remove(rname)
        os.remove(qname)


    def _is_binary_array(self, x):
        is_binary = True
        for u in x:
            if u != 0 and u != 1:
                is_binary = False
                break

        return is_binary
    
    def _append_X(self, feature_type, new_X, X, id_col, cur_feature, new_features=[], thresholds=None):
        if feature_type == "continuous":
            for sign in (">=", "<"):
                for point in thresholds:
                    if sign == ">=":
                        new_col = (np.expand_dims(X[:, id_col], axis=1) >= point).astype(np.int)
                        new_X = np.append(new_X, new_col, axis=1)
                    elif sign == "<":
                        new_col = (np.expand_dims(X[:, id_col], axis=1) < point).astype(np.int)
                        new_X = np.append(new_X, new_col, axis=1)

                    new_features.append(DiscretizedFeature(
                        	name="(X%d %s %f)" % (id_col, sign, point),
                        	source_feature=cur_feature,
                        	sign=sign,
                        	threshold=point
                        	))
                        
        elif feature_type == "binary":
            new_col = np.expand_dims(X[:, id_col], axis=1)
        
            new_X = np.append(new_X, new_col, axis=1)
            new_features.append(Feature(
            		name="X%d" % (id_col),
            		feature_type="binary"
            	))

            new_X = np.append(new_X, 1 - new_col, axis=1)
            new_features.append(Feature(
            		name="(NOT X%d)" % (id_col),
            		feature_type="binary"
            	))

        else:
            raise Exception("Make sure your training and test set only contains binary and continuous values.")
        
        return new_X
    
    def _preprocess_train(self, X, y):
        """
        Discretize continuous features and extend with its negation for already binary features
        Also make sure every features already have its negation in the data
        """
        new_X = np.zeros((X.shape[0], 0))
        raw_features = []
        new_features = []
        
        disc = Orange.preprocess.discretize.EntropyMDL()
        domain = Orange.data.Domain.from_numpy(X, y)
        orange_table = Orange.data.Table.from_numpy(domain, X, y)
        
        for i, attr in enumerate(orange_table.domain.attributes):
            if self._is_binary_array(X[:, i]):
                cur_feature = Feature(name="X%d" % i, feature_type="binary")
                new_X = self._append_X("binary", new_X, X, i, cur_feature, new_features)
                raw_features.append(cur_feature)
            else:
                disc_attr = disc(orange_table, attr)
                thresholds = disc_attr.compute_value.points
                cur_feature = Feature(name="X%d" % i, feature_type="continuous", thresholds=thresholds)
                new_X = self._append_X("continuous", new_X, X, i, cur_feature, new_features, thresholds)
                raw_features.append(cur_feature)

        return new_X, raw_features, new_features
    
    def _preprocess_test(self, X):
        assert(X.shape[1] == len(self.raw_features))
        
        new_X = np.zeros((X.shape[0], 0))
        for i, feature in enumerate(self.raw_features):
            if feature.feature_type == "binary":
                new_X = self._append_X("binary", new_X, X, i, feature)
            elif feature.feature_type == "continuous":
                new_X = self._append_X("continuous", new_X, X, i, feature, thresholds=feature.thresholds)
                
        return new_X
    
    def fit(self, X, y):
        """
        Parameters
        ----------
        X : 2D-array of shape (n_samples, n_features)
            Training data
        
        y : 1D-array of shape (n_samples,) with values 0/1
            Target class
        """
        X, raw_features, new_features = self._preprocess_train(X, y)
        n_features = X.shape[1]
        self.n_features = n_features
        self.raw_features = raw_features
        self.new_features = new_features
        
        self._maxsat_solve(X, y)
    
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
        
        X = self._preprocess_test(X)
        preds = np.matmul(X, self.B.T).prod(axis=1)
        
        return (preds > 0).astype(np.int)
    
    def _clause_to_str(self, clause):
        n_features = self.n_features
        new_features = self.new_features
        literals = [new_features[j].name for j in range(n_features) if clause[j] == 1]
        return "[" + " OR ".join(literals) + "]"
        
    def get_rule(self):
        unique_clauses = np.unique(self.B, axis = 0)
        rules_array = [self._clause_to_str(clause) for clause in unique_clauses if clause.size > 0]
        rule = " AND ".join(rules_array)
        return rule
    