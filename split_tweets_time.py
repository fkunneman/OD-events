#!/usr/bin/env python

import argparse
import datetime
from collections import defaultdict
import codecs

parser = argparse.ArgumentParser(description = "Program to sort tweets in time and make sequences of words")

parser.add_argument('-i', action = 'store', required = True, nargs='+', help = "the infiles")
parser.add_argument('-o', action='store', required=True, help = "the outfile")
parser.add_argument('-u', action = 'store', default = "day", choices = ["day","hour","minute"], help="specify the time unit to divide tweets by")
parser.add_argument('-d', action='store', default = 2, type = int, help = "the date column in the tweet")
parser.add_argument('-t', action='store', default = 3, type = int, help = "the time column in the tweet")

outfile = codecs.open(args.o,"w","utf-8")
word_timewindow = defaultdict(list)

#make time-tweet dict and word vocabulary
time_tweet = defaultdict(list)
words = []
for f in args.i:
    tweetfile = codecs.open(f,"r","utf-8")
    for tweet in tweetfile.readlines():
        tokens = tweet.strip().split("\t")
        date = tokens[args.d]
        time = tokens[args.t]
        tweet_datetime = time_functions.return_datetime(date,time = time,setting="vs")
        time_tweet[tweet_datetime].extend(tokens[-1].split(" "))
        words.extend(tokens[-1].split(" "))
vocabulary = list(set(words))

#sort tweets in time
sorted_time = sorted(time_tweet.keys())

#for each timepoint
starttime = sorted_time[0]
endtime = sorted_time[-1]
if args.u == "day":
    heap = datetime.timedelta(days=1)
elif args.u == "hour":
    heap = datetime.timedelta(hours=1)
elif args.u == "minute":
    heap = datetime.timedelta(minutes=1)
#count word and add to sequence
windowtime = starttime + heap
num_windows = (endtime-starttime) / heap
for word in vocabulary:
    word_timewindow[word] = num_windows * [0]
print word_timewindow
time = starttime
i = 0
w = 0
while windowtime <= endtime:
    wordcount = defaultdict(int)
    while time <= windowtime:
        tweets = time_tweet[time]
        for word in tweets:
            wordcount[word] += 1
        i += 1
        time = sorted_time[i]
    for word in wordcount.keys():
        word_timewindow[word][w] = wordcount[word]
    w += 1
    windowtime += heap

#write to file
for word in vocabulary:
    outfile.write(word + "\t" + "|".join(word_timewindow[word]) + "\n")
outfile.close()