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

print args.i
#make term nearest neighbor dict
infile = codecs.open(args.i,"r","utf-8")
lines = infile.readlines()
infile.close()
bursty_terms = lines[0].strip().split(" ")
similarities = [float(x) for x in lines[1].strip().split(" ")]
nns = sorted(range(len(similarities)), key=lambda ke: similarities[ke],reverse=True)
term_nearest_neighbours[bursty_terms[0]] = [bursty_terms[x] for x in nns[1:(1+args.k)]]
#print bursty_terms[0],nns,nns[:5],[bursty_terms[x] for x in nns[:5]]
print "extracting nearest neighbours for",len(bursty_terms),"bursty terms"
for line in lines[2:]:
    similarities = [float(x) for x in line.strip().split(" ")[1:]]
    nns = sorted(range(len(similarities)), key=lambda ke: similarities[ke],reverse=True)
    term_nearest_neighbours[line.split(" ")[0]] = [bursty_terms[x] for x in nns[1:(1+args.k)]]

print "extracting term links"
for term in bursty_terms:
    for neighbour in term_nearest_neighbours[term]:
        if term in term_nearest_neighbours[neighbour]:
            term_nearest_neighbours[neighbour].remove(term)
            term_links[term].append(neighbour)
            term_links[neighbour].append(term)

print "making clusters"
for term in term_links.keys():
    if term in term_clust.keys():
        clust = term_clust[term]
        clust_content = clust_terms[clust]
        clust_words = [x[0] for x in clust_content]
        for term2 in term_links[term]:
            if term2 in clust_words:
                index = clust_words.index(term2)
                clust_terms[clust][index][1] += 1
            else:
                clust_terms[clust].append((term2,1))
    else:
        candidates = [term2 for term2 in term_links[term] if term2 in term_clust.keys()]
        if len(candidates) == 1:
            term_clust[term] = term_clust[term2]
            clust_terms[term_clust[term2]].append((term,1))
        else:
            print candidates

    print clust_terms