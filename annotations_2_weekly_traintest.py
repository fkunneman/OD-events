
import sys
import datetime
import re
import os
from collections import defaultdict

annotations = open(sys.argv[1])
classifierdir = sys.argv[2]

#dict with date - number-label
date_annotations = defaultdict(list)
window_events = defaultdict(list)

d = re.compile(r'(\d{2})_(\d{2})_(\d+)')
for line in annotations.readlines():
    tokens = line.strip().split("\t")
    datesearch = d.search(tokens[0]).groups()
    date = datetime.date(2013,int(datesearch[0]),int(datesearch[1]))
    if len(tokens) == 4:
        if tokens[1] == tokens[2] and tokens[1] == '1':
            date_annotations[date].append((datesearch[2],'1'))
        else:
            date_annotations[date].append((datesearch[2],'0'))
    else:
        date_annotations[date].append((datesearch[2],tokens[1]))

i = 0
da_sorted = sorted(date_annotations.keys())
date = da_sorted[0]
while date < datetime.date(2013,8,10):
    for w in range(7):
        d = date + datetime.timedelta(days = w)
        window_events[i].extend(date_annotations[d])
    print i,date,d
    i += 1
    date = date + datetime.timedelta(days = 7)

quit()

outdir = classifier_dir + "week2/"
os.mkdir(outdir)
train = open(outdir + "train.txt","w")
test = open(outdir + "test.txt","w")



    
