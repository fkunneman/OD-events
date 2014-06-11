from __future__ import division
import sys
import re

#extract cluster-label-conf pairs
classifications_score = []
classifications = []
conf = re.compile(r"(0\.\d+)")
example_label = re.compile(r"Example (\d+) Label: (\d)")
el = []
els = False
for cl in sys.argv[2:]:
    classificationfile = open(cl)
    for line in classificationfile.readlines():
        if example_label.search(line):
            el = example_label.search(line).groups()
            els = True
        if re.search(r"^1:",line):
            if els:
                classifications.append([el[1],'1'])
                els = False
            c = conf.search(line).groups()[0]
            classifications_score.append([el[0],el[1],float(c)])
        if re.search(r"^0:",line) and els:
            classifications.append([el[1],'0'])
            els = False

    print len(classifications_score)
    classificationfile.close()

#sort by conf
classifications_score.sort(key = lambda x : x[2],reverse = True)

precision_at = [1,5,10,25,50,100,250,500,1000]
outfile = open(sys.argv[1],"w")
for i in precision_at:
    tp = len([x for x in classifications_score[:i] if x[1] == '1'])
    precision = tp / i
    outfile.write(str(i) + " " + str(precision) + "\n")
outfile.close()

tp = len([x for x in classifications if x[0] == '1' and x[1] == '1'])
fp = len([x for x in classifications if x[0] == '0' and x[1] == '1'])
fn = len([x for x in classifications if x[0] == '1' and x[1] == '0'])
precision = tp / (tp+fp)
recall = tp / (tp+fn)
f1 = 2 * ((pr*re) / (pr+re))
outfile.write("\n" + " ".join([precision,recall,f1]) + "\n")
