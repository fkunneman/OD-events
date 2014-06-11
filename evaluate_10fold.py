from __future__ import division
import sys
import re
import matplotlib.pyplot as plt
from pylab import *

#extract cluster-label-conf pairs
classifications_score = []
classifications = []
conf = re.compile(r"(0\.\d+)")
example_label = re.compile(r"Example (\d+) Label: (\d)")
el = []
els = False
for cl in sys.argv[4:]:
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
#plotfile = open(sys.argv[1],"w")
if int(sys.argv[3]):
x = []
y = []
for i,z in enumerate(classifications_score):
    if i > 0:
        tp = len([p for p in classifications_score[:i] if p[1] == '1'])
        precision = tp / i
        #plotfile.write(str(i) + " " + str(precision) + "\n")
        x.append(i)
        y.append(precision)

plt.plot(x,y,linewidth=3)
plt.ylabel('Precision')
plt.xlabel('Rank by classifier confidence')
plt.savefig(sys.argv[1],bbox_inches="tight")
#plotfile.close()

outfile = open(sys.argv[2],"w")
tp = len([x for x in classifications if x[0] == '1' and x[1] == '1'])
fp = len([x for x in classifications if x[0] == '0' and x[1] == '1'])
fn = len([x for x in classifications if x[0] == '1' and x[1] == '0'])
precision = tp / (tp+fp)
recall = tp / (tp+fn)
f1 = 2 * ((precision*recall) / (precision+recall))
outfile.write("\n" + " ".join([str(x) for x in [precision,recall,f1]]) + "\n")
outfile.close()
