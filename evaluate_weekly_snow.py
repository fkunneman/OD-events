from __future__ import division
import sys
import re

outfile = open(sys.argv[1],"w")

#extract cluster-label-conf pairs
classifications = []
#conf = re.compile(r"(0\.\d+)")
example_label = re.compile(r"Example (\d+) Label: (\d)")
for week in sys.argv[2:]:
    el = []
    els = False
    classifications = []
    num = week[-5]
    d = "/".join(week.split("/")[:-1]) + "/"
    classificationfile = open(d + snow + num + "/test.out")
    for line in classificationfile.readlines():
        if example_label.search(line):
            el = example_label.search(line).groups()
            els = True
        if re.search(r"^1:",line):
            if els:
                classifications.append([el[1],'1'])
                els = False
        if re.search(r"^0:",line) and els:
            classifications.append([el[1],'0'])
            els = False
            #c = conf.search(line).groups()[0]
            #classifications.append([el[0],el[1],float(c)])
    #print len(classifications_score)
    tp = len([x for x in classifications if x[0] == '1' and x[1] == '1'])
    fp = len([x for x in classifications if x[0] == '0' and x[1] == '1'])
    #fn = len([x for x in classifications if x[0] == '1' and x[1] == '0'])
    precision = tp / (tp+fp)
    #recall = tp / (tp+fn)
    #f1 = 2 * ((precision*recall) / (precision+recall))
    outfile.write(num + " " + str(precision) + "\n")

    classificationfile.close()

outfile.close()