#!/usr/bin/env python

import argparse
import codecs
from collections import defaultdict
import datetime
import re
import multiprocessing

import gen_functions

"""
Script to generate similarity graphs of bursty features
"""
parser = argparse.ArgumentParser(description = "Script to generate similarity graphs of bursty features")
parser.add_argument('-i', action = 'store', nargs='+',required = True, help = "The files with tweets per hour")  
parser.add_argument('-b', action = 'store', required = True, help = "the file with bursty unigrams")
# parser.add_argument('-t', action = 'store', required = True, help = "the file with term frequencies over time")
# parser.add_argument('-o', action = 'store', required = True, help = "the file to write the per-date similarity graph to")

args = parser.parse_args()


def count_terms(lines,queue):
    term_frequency = defaultdict(int)
    for line in lines:
        for term in line.split(" "):
            term_frequency[term] += 1
    queue.put(term_frequency)

def extract_tweets(tweets,terms,queue):
    term_words = defaultdict(list)
    for tweet in tweets:
        words = list(set(tweet.split(" ")))
        for term in terms:
            if term in words:
                term_words.extend(words)
    queue.put(term_words)


date_files = defaultdict(list)
date_burstyterms = defaultdict(list)

#cluster files by date
date = re.compile(r"(\d{4})(\d{2})(\d{2})-")
for f in args.i:
    dates = date.search(f).groups()
    date_files[datetime.date(int(dates[0]),int(dates[1]),int(dates[2]))].append(f)

#make date-burstyterm-graph
burstyfile = codecs.open(args.b,"r","utf-8")
date = re.compile(r"(\d{2})/(\d{2})/(\d{2})")
for line in burstyfile:
    tokens = line.strip().split("\t")
    dates = tokens[2].split(" ")
    for t in dates:
        d = date.search(t).groups()
        date_burstyterms[datetime.date(int("20" + d[0]),int(d[1]),int(d[2]))].append(tokens[0])

#for each date
for date in sorted(date_files.keys())[:1]:
    tweets = []
    #extract all tweets
    files = date_files[date]
    for f in files:
        tweets.extend([l.strip() for l in codecs.open(f,"r","utf-8").readlines()])

    #make vocabulary
    print "making vocabulary"
    q = multiprocessing.Queue()
    tweet_chunks = gen_functions.make_chunks(tweets,dist=True)
    for i in range(len(tweet_chunks)):
        p = multiprocessing.Process(target=count_terms,args=[tweet_chunks[i],q])
        p.start()

    ds = []
    while True:
        l = q.get()
        ds.append(l)
        if len(ds) == len(tweet_chunks):
            break
    term_frequency = defaultdict(int)
    for d in ds:
        for k in d:
            term_frequency[k] += d[k]
    term_index = {}
    i = 0
    for term in term_frequency.keys():
        if term_frequency[term] > 1:
        	term_index[term] = i
                i += 1

    #make burstyterm-tweet vectors
    burstyterms = date_burstyterms[date]
    print "making psuedo-docs"    
    #extract tweets containing term
    q = multiprocessing.Queue()
    term_chunks = gen_functions.make_chunks(burstyterms,dist=True)
    for i in range(len(term_chunks)):
        p = multiprocessing.Process(target=extract_tweets,args=[tweets,term_chunks[i],q])
        p.start()

    ds = []
    while True:
        l = q.get()
        ds.append(l)
        if len(ds) == len(term_chunks):
            break
    term_words = defaultdict(int)
    for d in ds:
        for k in d:
            term_words[k].extend(d[k])
    print term_words
    #generate vector

#generate combinations of vectors
#for each combination:
    #compute similarity


#extract term sub-window freq

