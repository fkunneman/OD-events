from __future__ import division
import sys
import re

outfile = open(sys.argv[1],"w")
devfile = open(sys.argv[2])
threshold = float(sys.argv[3])

#extract cluster-label-conf pairs
classifications = []
#conf = re.compile(r"(0\.\d+)")
example_label = re.compile(r"Example (\d+) Label: (\d)")
weeknum = int(sys.argv[1].split("/")[-2][-1])

#define threshold
#extract cluster-label-conf pairs
classifications_score = []
conf = re.compile(r"(0\.\d+)")
example_label = re.compile(r"Example (\d+) Label: (\d)")
el = []
for line in devfile.readlines():
    if example_label.search(line):
        el = example_label.search(line).groups()
    if re.search(r"^1:",line):
        c = conf.search(line).groups()[0]
        classifications_score.append([el[0],el[1],float(c)])

devfile.close()

#sort by conf
classifications_score.sort(key = lambda x : x[2],reverse = True)
rank_score_precision = []
rank_at_threshold = -1

#print classifications_score
for i,z in enumerate(classifications_score):
    if i > 0:
        tp = len([p for p in classifications_score[:i] if p[1] == '1'])
        precision = tp / i
#        print precision
        #plotfile.write(str(i) + " " + str(precision) + "\n")
        if precision > threshold:
            rank_at_threshold = i
            rank_score_precision.append([i,p[2],precision])

print rank_score_precision
conf_threshold = rank_score_precision[-1][1]

for i,week in enumerate(sys.argv[4:]):
    el = []
    #els = False
    classifications = []
    num = week[-5]
    d = "/".join(week.split("/")[:-1]) + "/"
    classificationfile = open(d + "snow" + num + "/test.out")
    for line in classificationfile.readlines():
        if example_label.search(line):
            el = example_label.search(line).groups()
            #els = True
        if re.search(r"^1:",line):
            c = conf.search(line).groups()[0]
            classifications_score.append([el[0],el[1],float(c)])
            #if els:
                #classifications.append([el[1],'1'])
                #els = False
        #if re.search(r"^0:",line) and els:
            #classifications.append([el[1],'0'])
            #els = False
            #c = conf.search(line).groups()[0]
            #classifications.append([el[0],el[1],float(c)])
    classificationfile.close()
    #sort by conf
    classifications_score.sort(key = lambda x : x[2],reverse = True)

    for i,z in enumerate(classifications_score):
        print z[2]
        if classifications_score[i][2] < conf_threshold:
            numbers = i-1
            tp = len([p for p in classifications_score[:i] if p[1] == '1'])
            precision = tp / i
            outfile.write(str(int(num) + weeknum + 1) + " " + str(numbers) + " " + str(precision) + "\n")
            break

    #print len(classifications_score)
    #tp = len([x for x in classifications if x[0] == '1' and x[1] == '1'])
    #fp = len([x for x in classifications if x[0] == '0' and x[1] == '1'])
    #fn = len([x for x in classifications if x[0] == '1' and x[1] == '0'])
    # precision = tp / (tp+fp)
    #recall = tp / (tp+fn)
    #f1 = 2 * ((precision*recall) / (precision+recall))
    

    

outfile.close()
