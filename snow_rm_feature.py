
import sys

testfile = open(sys.argv[1])
baseline1 = int(sys.argv[2])
baseline2 = int(sys.argv[3])
lines = testfile.readlines()
testfile.close()

for i in range(13):
    if baseline1 or baseline2:
        outfile = open("f" + str(i+2) + "_only/test.txt","w")
    else:
        outfile = open("f" + str(i+2) + "/test.txt","w")
    for l in lines:
        tokens = l.split(":")[0].split(",")
        if baseline1:
            outfile.write(tokens[2] + ":\n")
        elif baseline2:
            outfile.write(tokens[-1] + ":\n")
        else:
            del tokens[i]
            outfile.write(",".join(tokens) + ":\n")
