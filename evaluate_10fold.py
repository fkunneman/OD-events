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
for cl in sys.argv[3:]:
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

#precision_at = [1,5,10,25,50,100,250,500,1000]
plotfile = open(sys.argv[1],"w")
for i,x in enumerate(classifications_score):
    if i > 0:
        tp = len([x for x in classifications_score[:i] if x[1] == '1'])
        precision = tp / i
        plotfile.write(str(i) + " " + str(precision) + "\n")
plotfile.close()

outfile = open(sys.argv[2],"w")
tp = len([x for x in classifications if x[0] == '1' and x[1] == '1'])
fp = len([x for x in classifications if x[0] == '0' and x[1] == '1'])
fn = len([x for x in classifications if x[0] == '1' and x[1] == '0'])
precision = tp / (tp+fp)
recall = tp / (tp+fn)
f1 = 2 * ((precision*recall) / (precision+recall))
outfile.write("\n" + " ".join([str(x) for x in [precision,recall,f1]]) + "\n")
outfile.close()
