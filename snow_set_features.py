
import sys

testfile = open(sys.argv[1])
testout = open(sys.argv[2],"w")
features = [int(x) for x in sys.argv[3:]]
lines = testfile.readlines()
testfile.close()

for l in lines:
    tokens = l.split(":")[0].split(",")
    outfile.write(",".join([tokens[x-2] for x in features]) + ":\n")
outfile.close()
