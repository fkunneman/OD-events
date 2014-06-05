import sys
import re

classificationfile = open(sys.argv[1])
ic = open(sys.argv[2])

classifications = []
conf = re.compile(r"(0\.\d+)")
i = 0
for line in classificationfile:
    #tokens = line.strip().split(r"\s+")
    #print tokens
    if re.search(r"^1:",line):
#        print line,conf.search(line)
        c = conf.search(line).groups()[0]
        classifications.append([i,float(c)])
        i += 1
classificaitonsfile.close()

classifications.sort(key = lambda x : x[1],reverse=True)

index_cluster = {}
for i in ic.readlines():
    tokens = i.strip().split(" ")
    index_cluster[tokens[0]] = tokens[1]
ic.close()    

for c in classifications[:1000]:
    

