
import sys

testfile = open(sys.argv[1])
lines = testfile.readlines()
testfile.close()

for i in range(12):
    outfile = open("f" + str(i+2) + "/test.txt","w")
    for l in lines:
        tokens = l.split(":")[0].split(",")
        del tokens[i]
        outfile.write(",".join(tokens) + ":\n")