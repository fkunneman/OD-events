from __future__ import division
import sys
import re

#extract cluster-label-conf pairs
classifications = []
conf = re.compile(r"(0\.\d+)")
example_label = re.compile(r"Example (\d+) Label: (\d)")
el = []
for cl in sys.argv[2:]:
    classificationfile = open(cl)
    for line in classificationfile.readlines():
        if example_label.search(line):
            el = example_label.search(line).groups()
        if re.search(r"^1:",line):
            c = conf.search(line).groups()[0]
            classifications.append([el[0],el[1],float(c)])
    print len(classifications)
    classificationfile.close()

#sort by conf
classifications.sort(key = lambda x : x[2],reverse = True)

precision_at = [50,100,250,500,1000]
outfile = open(sys.argv[1],"w")
for i in precision_at:
    tp = len([x for x in classifications[:i] if x[1] == '1'])
    precision = tp / i
    outfile.write(str(i) + " " + str(precision) + "\n")
outfile.close()