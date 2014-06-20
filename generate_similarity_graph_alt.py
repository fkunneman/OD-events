#!/usr/bin/env python

from __future__ import division
import argparse
import codecs
from collections import defaultdict
import datetime
import re
import multiprocessing
import numpy
from sklearn.metrics import pairwise_distances
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from itertools import combinations

import gen_functions

"""
Script to generate similarity graphs of bursty features
"""
parser = argparse.ArgumentParser(description = "Script to generate similarity graphs of bursty features")  
# parser.add_argument('-b', action = 'store', required = True, help = "the file with bursty unigrams")
parser.add_argument('-t', action = 'store', required = True, help = "the file with term frequencies over time")
parser.add_argument('-i', action = 'store', nargs='+',required = False, help = "The files with tweets")
parser.add_argument('-w', action = 'store', required = True, help = "the file to write similarity files to")

args = parser.parse_args()

date_burstyterms = defaultdict(list)
date_seqs = defaultdict(lambda : defaultdict(list))

#1: make time segments
datetime_tweets = defaultdict(list)
#cluster files by date
vocabulary = []
datet = re.compile(r"(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})")
for f in args.i:
    dt = datet.search(f).groups()
    dto = datetime.datetime(int(dt[0]),int(dt[1]),int(dt[2]),int(dt[3]),int(dt[4]))
    o = codecs.open(f)
    for tweet in o.readlines():
        datetime_tweets[dto].append(tweet)

ordered_dates = sorted(datetime_tweets.keys())

#make term_sequence-graph
terms = []
seqfile = codecs.open(args.t,"r","utf-8")
for line in seqfile.readlines():
    tokens = line.strip().split("\t") 
    terms.append(tokens[0])
    # = [int(x) for x in tokens[1].split("|")]
seqfile.close()

#2: calculate sim
term_sims = defaultdict(lambda : defaultdict(float))
term_seqs = defaultdict(list)
term_tweets = defaultdict(list)
bd = ordered_dates[0]
n = bd + datetime.timedelta(minutes=15)
while bd <= ordered_dates[-1]:
    c = defaultdict(int)
    l = defaultdict(list)
    while bd <= n:
        print bd
        try:
            tweets = datetime_tweets[bd]
            print tweets
            for t in tweets:
                words = t.strip().split("\t")[-1].split(" ")
                print words
                for w in words:
                    c[w] += 1
                    l[w].extend(t.strip().split("\t")[-1].split(" "))
        except:
            print "nt"
        bd = bd + datetime.timedelta(minutes = 1)
    for term in terms:
        if term in c.keys():
            term_seqs[term].append(c[term])
            term_tweets[term].append(l[term])
        else:
            term_seqs[term].append(0)
            term_tweets[term].append([])
    n = n + datetime.timedelta(minutes = 15)

bursty_seqs = defaultdict(list)
for s in range(len(term_seqs[terms[0]])):
    bt_weight = {}
    #calculate weight for each bursty term
    for bt in terms:
        win = term_seqs[term]
        subwin = win[s]
        try:
            bt_weight[bt] = subwin/sum(win)
        except ZeroDivisionError:
            bt_weight[bt] = 0.0

    pseudodocs = []
    #calculate similarity between bursty terms
    for bt in terms:
        print bt,term_tweets[bt],term_tweets[bt][s]
        subwin = term_tweets[bt][s] 
        pseudodocs.append((bt," ".join(subwin)))

    #print "calculating similarities"
    tfidf_vectorizer = TfidfVectorizer()
    print pseudodocs
    tfidf_matrix = tfidf_vectorizer.fit_transform([x[1] for x in pseudodocs])
    cosim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    print "calculating feature-pair subwindow-scores"
    for c,term1 in enumerate(terms[:-1]):
        for term2 in terms[c:]:
            # if not bt_weight[term1] == 0.0 or bt_weight[term2] == 0.0:
            term_sims[term1][term2] += (bt_weight[term1] * bt_weight[term2] * cosim[terms.index(term1),terms.index(term2)])   

outfile = codecs.open(args.w,"w","utf-8")
print "printing similarities"
#print header
outfile.write(" ".join(terms) + "\n")
#print vals
for c,term1 in enumerate(terms[:-1]):
    if c > 0:
        outfile.write(term1 + " " + " ".join([str(term_sims[termpre][term1]) for termpre in terms[:c]]))
    outfile.write(" 1.0 ")
    outfile.write(" ".join([str(term_sims[term1][term2]) for term2 in terms[c+1:]]) + "\n")
outfile.write(burstyterms[-1] + " " + " ".join([str(term_sims[termpre][burstyterms[-1]]) for termpre in terms[:-1]]) + " 1.0\n")
outfile.close()
