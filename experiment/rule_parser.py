import sys

DATASET = sys.argv[1]
MODEL = sys.argv[2]
for i in range(10):
	with open("./{}/{}/result-{}-{}-{}.txt".format(DATASET, MODEL, MODEL, DATASET, i)) as f:
		for line in f.readlines():
			if line.startswith("t: best_model_rule_size (re"):
				print(line[49:], end="")

for i in range(10):
	with open("./{}/{}/result-{}-{}-{}.txt".format(DATASET, MODEL, MODEL, DATASET, i)) as f:
		fl = False
		for line in f.readlines():
			if fl:
				st = line[3:].replace(">=", "$\\geq$").replace("<", "$<$")
				print(st, end="")
				fl = False
			if line.startswith("t: best_model_rule (retrai"):
				fl = True