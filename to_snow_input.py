#!/usr/bin/env python

import argparse
import codecs
import re
from collections import defaultdict

"""
Script to convert feature weights to snow winnow classification input
"""
parser = argparse.ArgumentParser(description = "Script to convert feature weights to snow winnow classification input")
parser.add_argument('-i', action = 'store', nargs = '+', required = True, help = "the cluster-label files")  
parser.add_argument('-f', action = 'store', nargs = '+', required = True, help = "the cluster-feature files")
parser.add_argument('-t', action = 'store', required = True, help = "the train_outfile")
parser.add_argument('-w', action = 'store', required = True, help = "the test_outfile")
parser.add_argument('-r', action = 'store', required = True, help = "the index_clusterfile")

args = parser.parse_args()

cluster_label = {}
cluster_features = {}

datec = re.compile(r"annotations_(\d{2}_\d{2})\.txt")
for f in args.i:
    cluster_label_file = codecs.open(f,"r","utf-8")
    date = datec.search(f).groups()[0]
    for line in cluster_label_file.readlines():
        tokens = line.strip().split(" ")
        cluster_label[date + "_" + tokens[0]] = tokens[1]
    cluster_label_file.close()

datec = re.compile(r"2013-(\d{2}-\d{2})/")
for f in args.f:
    cluster_features_file = codecs.open(f,"r","utf-8")
    date = re.sub("-","_",datec.search(f).groups()[0])
    for line in cluster_features_file.readlines():
        tokens = line.strip().split("\t")
        cluster = date + "_" + tokens[0]
        features = tokens[2].split(",")
        cluster_features[cluster] = ",".join([str(i+2) + "(" + x + ")" for i,x in enumerate(features)])

trainfile = codecs.open(args.t,"w","utf-8")
for cluster in cluster_label.keys():
    trainfile.write(cluster_label[cluster] + "," + cluster_features[cluster] + ":" + "\n")
trainfile.close()
trainclusters = set(cluster_label.keys())

testfile = codecs.open(args.w,"w","utf-8")
indexfile = codecs.open(args.r,"w","utf-8")
index = 0
for cluster in cluster_features.keys():
    if not bool(set(cluster) & trainclusters):
        indexfile.write(str(index) + " " + cluster + "\n")
        index += 1
        testfile.write(cluster_features[cluster] + ":" + "\n")
testfile.close()
indexfile.close()


