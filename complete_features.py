#!/usr/bin/env python

import argparse
import codecs
import re
from collections import defaultdict

"""
"""
parser = argparse.ArgumentParser(description = "")
parser.add_argument('-i', action = 'store', nargs = '+', required = True, help = "the cluster-feature files")  
parser.add_argument('-w', action = 'store', required = True, help = "the term_wiki file")
parser.add_argument('-b', action = 'store', nargs = '+', required = True, help = "the term_burstiness files")

args = parser.parse_args()

date_term_burstiness = defaultdict(lambda : {})
term_newsworthiness = {}

#collect wiki-scores
wikifile = codecs.open(args.w,"r","utf-8")
for line in wikifile.readlines():
    tokens is line.strip().split("\t")
    term_newsworthiness[tokens[0]] = tokens[1]
wikifile.close()

#collect weights
for f in args.w:
    weightfile = codecs.open(f,"r","utf-8")
    date = re.sub(r"\'txt","",f.split("/")[-1])
    for line in weightfile.readlines():
        tokens = line.strip("\t")
        date_term_burstiness[date][tokens[0]] = tokens[1]
    weightfile.close()

#add to featurefiles
for f in args.i:
    directory = "/".join(f.split("/")[:-1]) + "/"
    fopen = codecs.open(f,"r","utf-8")
    fwrite = codecs.open(directory + "features_final.txt","w","utf-8")
    date = f.split("/")[-2]
    print "date",date
    for line in fopen.readlines():
        tokens = line.strip().split("\t")
        num_u = len(tokens[1].split(" "))
        features = tokens[2].split(",")
        features.append(str(num_u))
        features.extend([term_newsworthiness[x] for x in tokens[1].split(" ")])
        features.extend([date_term_burstiness[date][x] for x in tokens[1].split(" ")])
        print "features",features
        fwrite.write("\t".join(tokens[:-1] + "\t" + ",".join(features) + "\n"))
