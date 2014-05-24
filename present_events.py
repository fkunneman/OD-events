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
parser.add_argument('-f', action = 'store', nargs='+',required = True, help = "the file with event clusters")
parser.add_argument('-b', action = 'store', required = True, help = "the file with bursty scores per term")
parser.add_argument('-o', action = 'store', required = True, help = "the directory to write similarity files to")

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
for f in args.f:
    dates = date.search(f.split("/")[-1]).groups()
    infile = codecs.open(f,"r","utf-8")
    clusters = [x.strip() for x in infile.readlines()]
    infile.close()
    date_clusters[datetime.date(2013,int(dates[0]),int(dates[1]))] = clusters

print "making bursty term graph"
#make date-burstyterm-graph
burstyfile = codecs.open(args.b,"r","utf-8")
bursties = defaultdict(float)
for line in burstyfile.readlines():
    tokens = line.strip().split("\t")
    bursties[tokens[0]] = tokens[1]
burstyfile.close()

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

    print "calculating scores"
    #calculate scores
    cluster_scores = {}
    cluster_scores2 = {}
    cluster_scores3 = {}
    for i,cluster in enumerate(clusters):
        clustertweets = cluster[2]
        print clustertweets
        print cluster[1]
        popularity = len(clustertweets)
        user_frequency = len(list(set([ct.split("\t")[2] for ct in clustertweets])))
        tweets_text = [ct.split("\t")[5].split(" ") for ct in clustertweets]
        words = []
        for tt in tweets_text:
            words.extend(tt)
        informativeness = len(list(set(words))) / len(words)
        burstiness = sum(bursties[x] for x in cluster[1])
        cluster_scores[i] = popularity * user_frequency * tweets_text * burstiness
        cluster_scores2[i] = popularity * tweets_text * burstiness
        cluster_scores3[i] = tweets_text * user_frequency * burstiness

    #rank scores and print to file
    dicts = [cluster_scores,cluster_scores2,cluster_scores3]
    for i in range(3):
        ranked_clusters = sorted(dicts[i].items(), key=lambda x: x[1],reverse = True)
        outfile = codecs.open(args.o + "ranked_clusters_" + str(i) + ".txt","w","utf-8")
        for cluster in ranked_clusters:
            outfile.write(str(cluster[0]) + " " + str(cluster[1]) + " " + " ".join(clusters[cluster[0]][1]) + "\n" + "\n".join(clusters[cluster[0]][2][:10]) + "\n\n")






