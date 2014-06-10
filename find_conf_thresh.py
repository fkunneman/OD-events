from __future__ import division
import sys
import re

#extract cluster-label-conf pairs
classifications = []
conf = re.compile(r"(0\.\d+)")
example_label = re.compile(r"Example (\d{2}) Label: (\d)")
el = []
for c in sys.argv[1:]:
    classificationfile = open(c)
    for line in classificationfile.readlines():
        if example_label.search(line):
            el = example_label.search(line).groups()
        if re.search(r"^1:",line):
            c = conf.search(line).groups()[0]
            classifications.append([el[0],el[1],float(c)])
    classificationfile.close()

#sort by conf
classifications.sort(key = lambda x : x[2])

#relate conf to F1
conf_f1 = {}
for i,c in enumerate(classifications):
    tp = len[x for x in classifications[:(i+1)] if x == '1']
    fp = len[x for x in classifications[:(i+1)] if x == '0']
    tn = len[x for x in classifications[(i+1):] if x == '1']
    fn = len[x for x in classifications[(i+1):] if x == '0']
    pr = tp / (tp+fp)
    re = tp / (tp+fn)
    f1 = 2 * ((pr*re) / (pr+re))
    conf_f1[c[2]] = f1

print conf_f1
cf = sorted(conf_f1.items(), key=lambda x: x[1])
print cf 
