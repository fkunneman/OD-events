
import sys

infile = sys.argv[1]
outfile = open(sys.argv[2],"w")

inopen = open(infile)
lines = inopen.readlines()
inopen.close()

linessplit = []
for line in lines:
    nline = line.strip().split("\t")
    nline = [nline[0],nline[1],[float(x) for x in nline[2].split(",")]]
    linessplit.append(nline)

linessplit.sort(key=lambda x: x[2][1],reverse=True)
for line in linessplit:
    outfile.write("\t".join([line[0],line[1]]) + "\t" + ",".join([str(x) for x in line[2]]) + "\n")
outfile.close()
