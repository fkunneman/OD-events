#!/usr/bin/env python

import argparse
import codecs
from collections import defaultdict
import re
import numpy

"""
Script to cluster event terms out of a similarity graph
"""
parser = argparse.ArgumentParser(description = "Script to cluster event terms out of a similarity graph")
parser.add_argument('-i', action = 'store', required = True, help = "the file with the similarity graph")  
parser.add_argument('-k', action = 'store', type = int, required = True, help = "the k parameter")
parser.add_argument('-o', action = 'store', required = True, help = "the file to write clusters to")

args = parser.parse_args()

#make term nearest neighbor dict
infile = codecs.open(args.i,"r","utf-8")
lines = infile.readlines()
infile.close()
bursty_terms = lines[0].strip().split(" ")

#for line in lines[1:2]:
similarities = [float(x) for x in lines[1].strip().split(" ")]
nns = sorted(range(len(similarities)), key=lambda k: similarities[k],reverse=True)
print bursty_terms[0],nns,nns[:5],[bursty_terms[x] for x in nns[:5]]



#for each term:
    #for each nearest neighbor
        #check if term in NN's of nearest neighbor
        #if so: add to cluster

