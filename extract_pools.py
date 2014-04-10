#! /usr/bin/env python

#testcomment

from __future__ import division
import codecs
import sys
import multiprocessing
import datetime
from collections import defaultdict
import operator
import gzip
import re
import numpy
from pynlpl.statistics import levenshtein

import time_functions
import gen_functions

outdir = sys.argv[1]
retweet_removal = int(sys.argv[2])
date_column = int(sys.argv[3])
time_column = int(sys.argv[4])
infiles = sys.argv[5:]

pool_tweets = defaultdict(list)
pool_time = defaultdict(lambda : defaultdict(int))

def collect_data(files,quetext):
    ht_tweets = defaultdict(list)
    #ht_time = defaultdict(lambda : defaultdict(int))
    for f in files:
        print f
        if f[-2:] == "gz":
            infile = gzip.open(f,"rb")
        else:
            infile = codecs.open(f,"r","utf-8")
        # for each tweet
        for tweet in infile.readlines():
            if retweet_removal and re.search(r'( |^)RT ?',tweet.split("\t")[-1]):
                continue
            timeinfo = [tweet.split("\t")[date_column],tweet.split("\t")[time_column]]
            tweet_date = time_functions.return_datetime(timeinfo[0],time = timeinfo[1],minute = True,setting="vs")
            tweet_text = tweet.strip().split("\t")[-1]
            if re.search(r'#',tweet):
                for hashtag in re.findall(r' ?(#[^ \n]+) ?',tweet):
                    hashtag = hashtag.lower()
                    #ht_time[hashtag][tweet_date] += 1
                    ht_tweets[hashtag].append(tweet_text)
            else:
                hashtag = "less"
                #ht_time[hashtag][tweet_date] += 1
                ht_tweets[hashtag].append(tweet_text.decode('utf-8'))
        quetext.put(ht_tweets)
        #quetime.put(ht_time)
        infile.close()
        print "done",f

qe = multiprocessing.Queue()
#qi = multiprocessing.Queue()
procs = list()
chunks = gen_functions.make_chunks(infiles,12)
for chunk in chunks:
    p = multiprocessing.Process(target=collect_data,args=[chunk,qe])
    procs.append(p)
    p.start()

dse = []
#dst = []
while True:
    e = qe.get()
    #i = qi.get()
    dse.append(e)
    print len(dse)
    #dsi.append(i)
    if len(dse) == len(infiles):
        break

print "join"
for p in procs:
    p.join()

print "concat"
hashtag_tweets = defaultdict(list)
#hashtag_time = defaultdict(lambda : defaultdict(int))
for d in dse:
    for k in d:
        hashtag_tweets[k].extend(d[k])
#for d in dsi:
#    for k in d:
#        for t in k:
#            hashtag_time[k][t] += d[k][t] 

#make pools



#automatic labeling



#write pools
hashtags = hashtag_tweets.keys()
hashtags.remove("less")
for hashtag in hashtags:
    outfile = codecs.open(outdir + hashtag + ".txt","w","utf-8")
    outfile.write(" ".join([x.encode('utf-8') for x in hashtag_tweets[hashtag]]))
    outfile.close()
