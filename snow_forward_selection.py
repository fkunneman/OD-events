
import sys
import os
import re

top_feature = int(sys.argv[1])
test = sys.argv[2]
selection_dir = sys.argv[3]
outfile = open(sys.argv[4],"w")
all_features = set([int(x) for x in sys.argv[5:]])

def select_f(stage,feature_list):
    resultfiles = []
    d = selection_dir + "stage" + str(stage) + "/"
    os.mkdir(d)
    #for each combi
    for feature in list(all_features - set(feature_list)):
        combi = feature_list + [feature]
        testdir = d + "feature_" + str(feature) + "/"
        testf = testdir + "test.txt"
        tenfold = testdir + "tenfold/"
        results = testdir + "results.txt"
        resultfiles.append((combi,results))
        os.mkdir(testdir)
        os.mkdir(tenfold)
        os.system("python ~/OD-events/snow_set_features.py " + test + " " + testfile + " " + " ".join([str(x) for x in combi]))
        #classify
        os.system("python ~/OD-events/snow_10fold.py /vol/tensusers/fkunneman/exp/od-events/annotations/cluster_labels.txt "
            "/vol/tensusers/fkunneman/exp/od-events/snow/index_cluster.txt " + test + " " + tenfold + " /scratch/fkunneman/experiment1/ 0")
        #evaluate
        os.system("python ~/OD-events/evaluate_10fold.py " + tenfold + "pratplot.txt " + results + " " + tenfold + "fold_*/test.out")
    results = []
    highest = [0,0]
    for f in resultfiles:
        fileopen = open(f[1])
        result = fileopen.readlines()[1]
        fileopen.close()
        if result[-1] > highest[1]:
            highest = [f[0],result[-1]]
        scores = ",".join([str(x) for x in f[0]]) + result.strip().split(" ")
        results.append(scores)
    outfile.write("\n")
    for s in results:
        outfile.write(" ".join(s) + "\n")
    outfile.write("\n")
    if len(f[0]) < len(all_features):
        select_f(stage+1,highest[0])

select_f(1,[top_feature])


