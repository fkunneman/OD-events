
import sys
import datetime
import re
import os
from collections import defaultdict

annotations = open(sys.argv[1])
index_cluster = open(sys.argv[2])
test_large = open(sys.argv[3])
classifierdir = sys.argv[4]
default_train = sys.argv[5]

#dict with date - number-label
date_annotations = defaultdict(list)
window_events = defaultdict(list)
cluster_index = {}
index_features = {}

for line in index_cluster.readlines():
    tokens = line.strip().split(" ")
    cluster_index[tokens[1]] = int(tokens[0])
index_cluster.close()

for i,line in enumerate(test_large.readlines()):
    index_features[i] = line
test_large.close()

d = re.compile(r'(\d{2})_(\d{2})_(\d+)')
for line in annotations.readlines():
    tokens = line.strip().split("\t")
    datesearch = d.search(tokens[0]).groups()
    date = datetime.date(2013,int(datesearch[0]),int(datesearch[1]))
    if len(tokens) == 4:
        if tokens[1] == tokens[2] and tokens[1] == '1':
            print tokens[0],cluster_index[tokens[0]]
            date_annotations[date].append((cluster_index[tokens[0]],'1'))
        else:
            date_annotations[date].append((cluster_index[tokens[0]],'0'))
    else:
        date_annotations[date].append((cluster_index[tokens[0]],tokens[1]))
annotations.close()

i = 0
da_sorted = sorted(date_annotations.keys())
date = da_sorted[0]
while date < datetime.date(2013,8,22):
    for w in range(7):
        d = date + datetime.timedelta(days = w)
        window_events[i].extend(date_annotations[d])
    print i,date,d
    i += 1
    date = date + datetime.timedelta(days = 7)

for week in range(i):
    outdir = classifierdir + "week_" + str(week) + "/"
    try: 
        os.mkdir(outdir)
    except:
        print "exists"
    os.system("cat " + default_train + " > " + outdir + "train.txt")
    train = open(outdir + "train.txt","a")
    for w in range(0,(week+1)):
        for cluster in window_events[w]:
            train.write(cluster[1] + "," + index_features[cluster[0]])
    for j,t in enumerate(range((week+1),i)):
        test = open(outdir + "test" + str(j) + ".txt","w")
        for cluster in window_events[t]:
            test.write(cluster[1] + "," + index_features[cluster[0]])
        test.close()
    train.close()




    
