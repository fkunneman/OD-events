#! /usr/bin/env python

#testcomment

import sys
import multiprocessing
from __future__ import division
import datetime
from collections import defaultdict
import operator
import gzip
import re
import numpy
from pynlpl.statistics import levenshtein

import time_functions
import gen_functions

outfile_frame = sys.argv[1]
retweet_removal = int(sys.argv[2])
date_column = int(sys.argv[3])
time_column = int(sys.argv[4])
infiles = sys.argv[5:]

pool_tweets = defaultdict(list)
pool_time = defaultdict(lambda : defaultdict(int))

def collect_data(files,quetime,quetext):
    ht_tweets = defaultdict(int)
    ht_time = defaultdict(lambda : defaultdict(int))
    for f in infiles:
        print f
        if f[-2:] == "gz":
            infile = gzip.open(f,"rb")
        else:
            infile = open(f)
        # for each tweet
        for tweet in infile.readlines():
            if retweet_removal and re.search(r'( |^)RT ?',tweet.split("\t")[-1]):
                continue
            timeinfo = [tweet.split("\t")[date_column],tweet.split("\t")[time_column]]
            tweet_date = time_functions.return_datetime(timeinfo[0],time = timeinfo[1],minute = True,setting="vs")
            tweet_text = tweet.split("\t")[-1]
            if re.search(r'#',tweet):
                for hashtag in re.findall(r' ?(#[^ \n]+) ?',tweet):
                    hashtag = hashtag.lower()
                    ht_time[hashtag][tweet_date] += 1
                    ht_tweets[hashtag].append(tweet_text)
            else:
                hashtag = "less"
                ht_time[hashtag][tweet_date] += 1
                ht_tweets[hashtag].append(tweet_text)
        quetext.put(ht_tweets)
        quetime.put(ht_time)
        f.close()

qe = multiprocessing.Queue()
qi = multiprocessing.Queue()
chunks = gen_functions.make_chunks(infiles,12)
for chunk in chunks:
    p = multiprocessing.Process(target=collect_data,args=[chunk,qe,qi])
    p.start()

dse = []
dst = []
while True:
    e = qe.get()
    i = qi.get()
    dse.append(e)
    dsi.append(i)
    if len(dsi) == len(chunks):
        break

hashtag_tweets = defaultdict(int)
hashtag_time = defaultdict(lambda : defaultdict(int))
for d in dse:
    for k in d:
        hashtag_tweets[k].extend(d[k])
for d in dsi:
    for k in d:
        for t in k:
            hashtag_time[k][t] += d[k][t] 

#make pools



#automatic labeling



#write pools

