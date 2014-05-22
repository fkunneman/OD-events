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

term_nearest_neighbours = defaultdict(list)
term_links = defaultdict(list)

term_clust = defaultdict(list)
clust_terms = []

#make term nearest neighbor dict
infile = codecs.open(args.i,"r","utf-8")
lines = infile.readlines()
infile.close()
bursty_terms = lines[0].strip().split(" ")
similarities = [float(x) for x in lines[1].strip().split(" ")]
nns = sorted(range(len(similarities)), key=lambda ke: similarities[ke],reverse=True)
term_nearest_neighbours[bursty_terms[0]] = [bursty_terms[x] for x in nns[1:(1+args.k)]]
#print bursty_terms[0],nns,nns[:5],[bursty_terms[x] for x in nns[:5]]
for line in lines[2:]:
    similarities = [float(x) for x in line.strip().split(" ")[1:]]
    nns = sorted(range(len(similarities)), key=lambda ke: similarities[ke],reverse=True)
    term_nearest_neighbours[line.split(" ")[0]] = [bursty_terms[x] for x in nns[1:(1+args.k)]]

for term in bursty_terms:
    for neighbor in term_nearest_neighbours[term]:
        if term in term_nearest_neighbours[neighbour]:
            term_nearest_neighbours[neighbour].remove(term)
            term_links[term].append(neighbour)
            term_links[neighbour].append(term)

print term_links


        #check if term in NN's of nearest neighbor
        #if so: add to cluster

