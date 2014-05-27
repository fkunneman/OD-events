#!/usr/bin/env python

import argparse
import codecs
from collections import defaultdict
import re
import numpy
from operator import itemgetter

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
term_termsims = defaultdict(lambda : defaultdict(float))

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
    tnn = [bursty_terms[x] for x in nns[1:(1+args.k)]]
    term = line.split(" ")[0]
    term_nearest_neighbours[term] = tnn
    for neigh in nns[1:(1+args.k)]:
        neighterm = bursty_terms[neigh]
        term_termsims[term][neighterm] = similarities[neigh]
        term_termsims[neighterm][term] = similarities[neigh]

print "extracting term links"
for term in bursty_terms:
    for neighbour in term_nearest_neighbours[term]:
        if term in term_nearest_neighbours[neighbour]:
            term_nearest_neighbours[neighbour].remove(term)
            term_links[term].append(neighbour)
            term_links[neighbour].append(term)

print "making clusters"
clust_index = 0
term_clust = {}
clust_terms = []
for term in term_links.keys():
    cluster = term_links[term] + [term]
    if len(cluster) > 1:
        candidates = list(set(cluster) & set(term_clust.keys()))
        if len(candidates) == 0: #total new cluster
            for cterm in cluster:
                term_clust[cterm] = clust_index
            clust_terms.append([[x,1] for x in cluster])
            clust_index += 1
        else:
            candidate_nums = list(set([term_clust[x] for x in candidates]))
            clust_num = candidate_nums[0]
            other = list(set(term_links[term]) - set(term_clust.keys()))
            if len(list(set(candidate_nums))) > 1: #different clusters
                #combine clusters
                for cn in candidate_nums[1:]:
                    clust_terms[clust_num].extend(clust_terms[cn])
                    for ct in clust_terms[cn]:
                        term_clust[ct[0]] = clust_num
                for cn in sorted(candidate_nums[1:],reverse=True):
                    clust_terms.pop(cn)
                    clust_index -= 1
                    for c in [x for x in term_clust.keys() if term_clust[x] > cn]:
                        term_clust[c] -= 1
                    if cn < clust_num:
                        clust_num -= 1
            for cterm in candidates:
                index = [x[0] for x in clust_terms[clust_num]].index(cterm)
                clust_terms[clust_num][index][1] += 1
            for cterm in other:
                term_clust[cterm] = clust_num
            clust_terms[clust_num].extend([[x,1] for x in other])

#write clusters
outfile = codecs.open(args.o,"w","utf-8")
for i,clust in enumerate(clust_terms):
    all_sims = []
    for j,term in enumerate(clust):
        sims = []
        neighs = term_termsims[term[0]].keys()
        for neigh in list(set(neighs) & set([x[0] for x in clust])):
            sims.append(term_termsims[term[0]][neigh])
            all_sims.append(term_termsims[term[0]][neigh])
        sim = sum(sims)/len(sims)
        clust[j].append(sim)
    mean_sim = sum(all_sims)/len(all_sims)
    clust.sort(key=lambda k: (k[1],k[2]), reverse=True)
    outfile.write(str(mean_sim) + "\t" + "\t".join(" ".join([t[0],str(t[1]),str(t[2])]) for t in clust) + "\n")
outfile.close()
