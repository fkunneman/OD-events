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
Script to rank and summarize the extracted events on a day
"""
parser = argparse.ArgumentParser(description = "Script to rank and summarize the extracted events on a day")
parser.add_argument('-i', action = 'store', nargs='+',required = True, help = "The files with tweets per hour")  
parser.add_argument('-c', action = 'store', nargs='+',required = True, help = "the file with event clusters")
#parser.add_argument('-t', action = 'store', required = True, help = "the file with term frequencies over time")
#parser.add_argument('-o', action = 'store', required = True, help = "the directory to write similarity files to")

args = parser.parse_args()

date_files = defaultdict(list)
date_clusters = defaultdict(list)

def extract_tweets(tweets,clusters,queue):
    cluster_tweets = defaultdict(list)
    for tweet in tweets:
        words = list(set(tweet.split("\t")[-1].split(" ")))
        for cluster in clusters:
            if bool(set(words) & set(cluster[1])):
                cluster_tweets[cluster[0]].append(tweet)
    queue.put(cluster_tweets)

#cluster files by date
date = re.compile(r"(\d{4})(\d{2})(\d{2})-")
for f in args.i:
    dates = date.search(f).groups()
    date_files[datetime.date(int(dates[0]),int(dates[1]),int(dates[2]))].append(f)

#make date-cluster dict
date = re.compile(r"(\d{1})-(\d{1,2})\.txt")
for f in args.c:
    dates = date.search(f.split("/")[-1]).groups()
    infile = codecs.open(f,"r","utf-8")
    clusters = [x.strip() for x in infile.readlines()]
    infile.close()
    date_clusters[datetime.date(2013,int(dates[0]),int(dates[1]))] = clusters

#for each date
for j,date in enumerate(sorted(date_files.keys())):
    print date
    #collect tweets
    tweets = []
    for f in date_files[date]:
        infile = codecs.open(f,"r","utf-8")
        tweets.extend([l.strip() for l in infile.readlines()])
        infile.close()
    #extract clusters
    clusters = []
    for i,line in enumerate(date_clusters[date]):
        clusters.append([i,[x.split(" ")[0] for x in line.split("\t")]])
    #link clusters to tweets
    print "extracting tweets"    
    q = multiprocessing.Queue()
    cluster_chunks = gen_functions.make_chunks(clusters,dist=True)
    for i in range(len(cluster_chunks)):
        p = multiprocessing.Process(target=extract_tweets,args=[tweets,cluster_chunks[i],q])
        p.start()

    ds = []
    while True:
        l = q.get()
        ds.append(l)
        for clustind in l.keys():
            clusters[clustind].append(l[clustind])
        if len(ds) == len(cluster_chunks):
            break

    print clusters

    # clustertweets = [0] * len()
    # index_cluster = {}
    # y = 0
    # for d in ds:
    #     for k in d:
    #         index_cluster[k] = y
    #         y += 1
    #         cluster_tweets.append(d[k])))
    # #compute similarities
    # print "calculating similarities"
    # tfidf_vectorizer = TfidfVectorizer()
    # tfidf_matrix = tfidf_vectorizer.fit_transform([x[1] for x in pseudodocs])
    # cosim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    # print "calculating feature-pair subwindow-scores"
    # for c,term1 in enumerate(sorted(index_term.keys()[:-1])):
    #     for term2 in sorted(index_term.keys()[c:]):
    #         # if not bt_weight[term1] == 0.0 or bt_weight[term2] == 0.0:
    #         term_sims[term1][term2] += (bt_weight[term1] * bt_weight[term2] * cosim[index_term[term1],index_term[term2]])

    # #print sims
    # outfile = codecs.open(args.o + str(date.month) + "-" + str(date.day) + ".txt","w","utf-8")
    # print "printing similarities"
    # #print header
    # outfile.write(" ".join(burstyterms) + "\n")
    # #print vals
    # for c,term1 in enumerate(burstyterms[:-1]):
    #     if c > 0:
    #         outfile.write(term1 + " " + " ".join([str(term_sims[termpre][term1]) for termpre in burstyterms[:c]]))
    #     outfile.write(" 1.0 ")
    #     outfile.write(" ".join([str(term_sims[term1][term2]) for term2 in burstyterms[c+1:]]) + "\n")
    # outfile.write(burstyterms[-1] + " " + " ".join([str(term_sims[termpre][burstyterms[-1]]) for termpre in burstyterms[:-1]]) + " 1.0\n")
    # outfile.close()
