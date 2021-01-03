import sys

for line in sys.stdin:
	dd = eval(line)
	print("({}, {}, {}, {})".format(dd['lamda'], dd['n_clause'], dd['rule_type'], dd['n_partitions']))
