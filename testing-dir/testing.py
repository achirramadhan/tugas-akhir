import sys
sys.path.insert(1, '/root/skripsi/imli')
print(sys.path)

import os
os.environ["PATH"] += os.pathsep + "/root/skripsi/open-wbo"
print(os.environ["PATH"])
os.system('open-wbo')

from IMLI import IMLI
imli = IMLI(n_clauses=2, lamda=2, solver="open-wbo", n_partitions=1)
