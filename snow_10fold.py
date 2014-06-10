
import sys
import datetime
import re
import os
from collections import defaultdict

annotations = open(sys.argv[1])
index_cluster = open(sys.argv[2])
test_large = open(sys.argv[3])
classifierdir = sys.argv[4]
expdir = sys.argv[5]
lax = int(sys.argv[6])

os.chdir(expdir)
#dict with date - number-label
event_label = []
cluster_index = {}
index_features = {}

for line in index_cluster.readlines():
    tokens = line.strip().split(" ")
    cluster_index[tokens[1]] = int(tokens[0])
index_cluster.close()

for i,line in enumerate(test_large.readlines()):
    index_features[i] = line
test_large.close()

for line in annotations.readlines():
    tokens = line.strip().split("\t")
    if len(tokens) == 4:
        if tokens[1] == tokens[2] and tokens[1] == '1':
            event_label.append((cluster_index[tokens[0]],'1'))
        else:
            if lax:
                if tokens[1] == '1' or tokens[2] == '1':
                    event_label.append((cluster_index[tokens[0]],'1'))
                else:
                    event_label.append((cluster_index[tokens[0]],'0'))
            else:
                event_label.append((cluster_index[tokens[0]],'0'))
    else:
        if tokens[1] == '1':
            event_label.append((cluster_index[tokens[0]],tokens[1]))
        else:
            event_label.append((cluster_index[tokens[0]],'0'))
annotations.close()

bs = re.compile(r"p-([\d\.]+)=d-([\d\.]+)=t-([\d\.]+)=c-(\d+)=r-(\d+)=s-([\d\.]+)")
#sort instances based on their label       
sorted_instances = sorted(event_label, key = lambda k: k[1])
#make folds based on taking the n-th instance as test
size = len(sorted_instances)
for i in range(10):
    outdir = classifierdir + "fold_" + str(i) + "/"
    try:
        os.mkdir(outdir)
    except:
        print "exists"
    train = sorted_instances[:]
    print len(sorted_instances)
    test = []
    j = i
    offset = 0
    while j < size:
        test.append(sorted_instances[j])
        #print i,j-offset,len(train_test["train"]),j,size,len(sorted_instances)
        del train[j-offset]
        j += 10
        offset += 1
    #classify
    print len(train),len(test)
    trainf = open(outdir + "train.txt","w")
    testf = open(outdir + "test.txt","w")
    for cluster in train:
        trainf.write(cluster[1] + "," + index_features[cluster[0]])
    for cluster in test:
        testf.write(cluster[1] + "," + index_features[cluster[0]])
    trainf.close()
    testf.close()

    os.system("cp " + outdir + "train.txt" + " .")
    os.system("cp " + outdir + "test.txt" + " .")
    os.system("paramsearch winnow train.txt 2")
    param = open("train.txt.winnow.bestsetting")
    paramline = param.read()
    param.close()
    params = bs.search(paramline).groups()
    print "snow -train -I " + train + " -F test.net -W " + params[0] + "," + params[1] + "," + params[2] + "," + params[3] + ":0-1 -r " + params[4] + " -S " + params[5]
    os.system("snow -train -I train.txt -F test.net -W " + params[0] + "," + params[1] + "," + params[2] + "," + params[3] + ":0-1 -r " + params[4] + " -S " + params[5])
    os.system("snow -test -I test.txt -F test.net -o allactivations > test.out")
    os.system("mv *  " + outdir)
