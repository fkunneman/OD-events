#!/usr/bin/env python

from __future__ import division
import argparse
import codecs
import os
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
        words = list(set(tweet.split("\t")[-1].lower().split(" ")))
        for cluster in clusters:
            terms = [x[0] for x in cluster[2]]
            if len(set(words) & set(terms)) > (len(terms) / 3) * 2:
                tokens = tweet.split("\t")
                if tokens[0] == "dutch":
                    words = tokens[-1].split(" ")
                    hashtags = len([x for x in words if re.search("^#",x)])
                    urls = len([x for x in words if re.search("^http://",x)])
                    if re.search("^@",words[0]):
                        reply = 1
                    else:
                        reply = 0
                    mentions = len([x for x in words[1:] if re.search("^@",x)])
                    cluster_tweets[cluster[0]].append([len(set(words) & set(terms)),hashtags,urls,reply,mentions,tokens[2],tokens[-1]])                
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
bursties = {}
for line in burstyfile.readlines():
    tokens = line.strip().split("\t")
    bursties[tokens[0]] = float(tokens[1])
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
        units = line.split("\t")
        mean_sim = units[0]
        terms = [x.split(" ") for x in units[1:]]
        clusters.append([i,mean_sim,terms])
    #link clusters to tweets
    print "extracting tweets"    
    q = multiprocessing.Queue()
    tweet_chunks = gen_functions.make_chunks(tweets,dist=True)
    for i in range(len(tweet_chunks)):
        p = multiprocessing.Process(target=extract_tweets,args=[tweet_chunks[i],clusters,q])
        p.start()

    ds = []
    while True:
        l = q.get()
        ds.append(l)
        for clustind in l.keys():
            l[clustind].sort(key=lambda x : x[0],reverse=True)
            #print l[clustind]
            clusters[clustind].append(l[clustind])
        if len(ds) == len(tweet_chunks):
            break

#    print clusters
    print "calculating scores"
    #calculate scores
    if not os.path.isdir(args.o + str(date) + "/"):
        os.mkdir(args.o + str(date) + "/")
    outstats = codecs.open(args.o + str(date) + "/clusterstats_tweets.txt","w","utf-8")
    outtweets = codecs.open(args.o + str(date) + "/clustertweets_ranked.txt","w","utf-8")
    for i,cluster in enumerate(clusters):
        print "cluster",i
        try:
            clusterterms = cluster[2]
            clustertweets = cluster[3]
        except:
            continue
        avg_links = sum([int(x[1]) for x in clusterterms]) / len(clusterterms)
        avg_sim = float(cluster[1])
        popularity = len(clustertweets) / len(tweets)
        tweets_text = [ct[-1].split("\t")[-1].split(" ") for ct in clustertweets]
        words = []
        for tt in tweets_text:
            words.extend(tt)
        informativeness = len(list(set(words))) / len(words)
        users = [ct[5] for ct in clustertweets]
        user_frequency = len(list(set(users))) / len(users)
        hashtags = sum([ct[1] for ct in clustertweets]) / len(clustertweets)
        urls = sum([ct[2] for ct in clustertweets]) / len(clustertweets)
        replies = sum([ct[3] for ct in clustertweets]) / len(clustertweets)
        mentions = sum([ct[4] for ct in clustertweets]) / len(clustertweets)
        avg_terms = sum([ct[0] for ct in clustertweets]) / len(clustertweets)
        outstats.write(str(i) + "\t" + " ".join([x[0] for x in clusterterms]) + "\t" + ",".join([str(x) for x in [avg_links,avg_sim,popularity,informativeness,user_frequency,hashtags,urls,replies,mentions,avg_terms]]) + "\n")
        outtweets.write("\n".join([str(i) + "\t" + " ".join(x) for x in tweets_text]) + "\n")

#     #rank scores and print to file
#     dicts = [cluster_scores,cluster_scores2,cluster_scores3,cluster_scores4,cluster_scores5]
#     #datename = args.f.split("/")[-1]
#     try:
#         os.mkdir(args.o + str(date) + "/")
#     except OSError:
#         print "exists"
#     for i in range(5):
#         ranked_clusters = sorted(dicts[i].items(), key=lambda x: x[1],reverse = True)
#         outfile = codecs.open(args.o + str(date) + "/ranked_clusters_" + str(i) + ".txt","w","utf-8")
#         for cluster in ranked_clusters:
# #            print cluster
#             outfile.write(str(cluster[0]) + " " + str(cluster[1]) + " " + " ".join(clusters[cluster[0]][1]) + "\n" + "\n".join([x[1].split("\t")[-1] for x in clusters[cluster[0]][2][:10]]) + "\n\n")






