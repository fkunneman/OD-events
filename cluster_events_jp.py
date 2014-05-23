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
clust_index = 0
term_clust = {}
clust_terms = []
for term in term_links.keys():
    #print term,term_links[term]
    cluster = term_links[term]
    if len(cluster) > 1:
        # print cluster
        # print term_clust
        # print [[i,l] for i,l in enumerate(clust_terms)]
    # print "cluster size",len(cluster)
        candidates = list(set(cluster) & set(term_clust.keys()))
        #print term_clust.keys(),term_links[term],candidates
        if len(candidates) == 0: #total new cluster
            for cterm in cluster:
                term_clust[cterm] = clust_index
            clust_terms.append([[x,1] for x in cluster])
            print candidates,clust_index,len(clust_terms)
            clust_index += 1
        else:
            candidate_nums = list(set([term_clust[x] for x in candidates]))
            clust_num = candidate_nums[0]
            print candidates, candidate_nums,clust_terms[clust_num]
            other = list(set(term_links[term]) - set(term_clust.keys()))
            if len(list(set(candidate_nums))) > 1: #different clusters
                #combine clusters
                #print "before",candidate_nums,clust_terms[clust_num],[[x,term_clust[x]] for x in candidates]
                for cn in candidate_nums[1:]:
                    clust_terms[clust_num].extend(clust_terms[cn])
                for cn in sorted(candidate_nums[1:],reverse=True):
                    clust_terms.pop(cn)
                    clust_index -= 1
                    for c in [x for x in term_clust.keys() if term_clust[x] > cn]:
                        term_clust[c] -= 1
     #                   try:
     #                       print unicode(c),term_clust[c]+1,"minus 1"
     #                   except:
     #                       print term_clust[c]+1,"minus 1"
                    if cn < clust_num:
                    #    for c in [x for x in candidates if term_clust[x] == clust_num]:
                    #        term_clust[c] -= 1
                        clust_num -= 1
                for c in [x for x in candidates if term_clust[x] in candidate_nums[1:]]:
                   term_clust[c] = clust_num
                #print "after",candidate_nums,clust_terms[clust_num],[[x,term_clust[x]] for x in candidates]
            for cterm in candidates:
                index = [x[0] for x in clust_terms[clust_num]].index(cterm)
                clust_terms[clust_num][index][1] += 1
            for cterm in other:
                term_clust[cterm] = clust_num
            clust_terms[clust_num].extend([[x,1] for x in other])



            #combine with other clusters
            

            
        #     if len(list(set(candidate_nums))) == 1: # all candidates are in same cluster 
        #         clust_num = term_clust[candidates[0]]
        #         term_clust[term] = term_clust[candidates[0]]
        #         clust = term_clust[term]
        # if len(cclusts) == 1: # all candidates are in same cluster 
        #     #print cclusts,cclusts[0],term_clust[cclusts[0]]
        #     clust_terms[clust].append([term,1])
        #     #print clust_terms,clust_words
        # else:
        #     for c in candidates[1:]:
        #         term_clust[c] = term_clust[term]
        #     clust_terms[clust].append([term,1])
        #     for c in cclusts:
        #         clust_terms[clust].extend(clust_terms[c])
        # clust_words = [x[0] for x in clust_terms[clust]]
        # for cand in candidates:
        #     #print cand
        #     index = clust_words.index(cand)
        #     clust_terms[clust][index][1] += 1
        # for ncand in not_candidates:
        #     clust_terms[clust].append([ncand,1])
        #     term_clust[ncand] = clust



#     if term in term_clust.keys():
#         clust = term_clust[term]
#         clust_content = clust_terms[clust]
#         clust_words = [x[0] for x in clust_content]
#         index = clust_words.index(term)
#         clust_terms[clust][index][1] += 1
# #        print term_links[term],clust_words
#         for term2 in term_links[term]:
#             if term2 in clust_words:
#                 index = clust_words.index(term2)
#                 clust_terms[clust][index][1] += 1
#             else:
#                 clust_terms[clust].append([term2,1])
#                 term_clust[term2] = clust
# #        print clust_terms[clust]
#     else:
#         candidates = list(set(term_links[term]) & set(term_clust.keys()))
#         #print term_clust.keys(),term_links[term],candidates
#         if len(candidates) == 0: #total new cluster
#             term_clust[term] = clust_index
#             for new in term_links[term]:
#                 term_clust[new] = clust_index
#             clust_index += 1
#             clust_terms.append([[term,1]] + [[x,1] for x in term_links[term]])
#         else:
#             cclusts = list(set([term_clust[x] for x in candidates]))
#             not_candidates = list(set(term_links[term]) - set(term_clust.keys()))
# #            print not_candidates
#             #print candidates,cclusts,len(cclusts)
#             term_clust[term] = term_clust[candidates[0]]
#             clust = term_clust[term]
#             if len(cclusts) == 1: # all candidates are in same cluster 
#                 #print cclusts,cclusts[0],term_clust[cclusts[0]]
#                 clust_terms[clust].append([term,1])
#                 #print clust_terms,clust_words
#             else:
#                 for c in candidates[1:]:
#                     term_clust[c] = term_clust[term]
#                 clust_terms[clust].append([term,1])
#                 for c in cclusts:
#                     clust_terms[clust].extend(clust_terms[c])
#             clust_words = [x[0] for x in clust_terms[clust]]
#             for cand in candidates:
#                 #print cand
#                 index = clust_words.index(cand)
#                 clust_terms[clust][index][1] += 1
#             for ncand in not_candidates:
#                 clust_terms[clust].append([ncand,1])
#                 term_clust[ncand] = clust
    #print clust_terms

for i,clust in enumerate(clust_terms):
   print "cluster",i
   for t in sorted(clust,key=itemgetter(1)):
       print t[0],t[1]
   print "\n"


