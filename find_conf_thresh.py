from __future__ import division
import sys
import re

#extract cluster-label-conf pairs
classifications = []
conf = re.compile(r"(0\.\d+)")
example_label = re.compile(r"Example (\d+) Label: (\d)")
el = []
for cl in sys.argv[1:]:
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

#relate conf to F1
conf_f1 = {}
for i,c in enumerate(classifications):
    tp = len([x for x in classifications[:(i+1)] if x[1] == '1'])
    fp = len([x for x in classifications[:(i+1)] if x[1] == '0'])
    tn = len([x for x in classifications[(i+1):] if x[1] == '1'])
    fn = len([x for x in classifications[(i+1):] if x[1] == '0'])
    #if (tp + fp) > 0:
#    print tp,fp,tn,fn
    pr = tp / (tp+fp)
#    ra = (i+1) / len(classifications)
#    conf_f1[c[2]] = (pr*3)*ra 
    #else:
    re = tp / (tp+fn)
    try:
        f1 = 2 * ((pr*re) / (pr+re))
    except ZeroDivisionError:
        f1 = 0
    conf_f1[c[2]] = pr

#print conf_f1
cf = sorted(conf_f1.items(), key=lambda x: x[1],reverse=True)
for c in cf:
    print c[0],c[1]

