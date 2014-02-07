#! /usr/bin/env python

import sys
import datetime
from collections import defaultdict
import gzip
import re
from pynlpl.statistics import levenshtein

import time_functions

outfile = sys.argv[1]
date_column = int(sys.argv[2])
time_column = int(sys.argv[3])
infiles = sys.argv[4:]

# make hashtag frequency list
hashtag_frequency = defaultdict(int)
hashtag_time = defaultdict(lambda : defaultdict(int))
for f in infiles:
    print f
    if f[-2:] == "gz":
        infile = gzip.open(f,"rb")
    else:
        infile = open(f)
    # for each tweet
    for tweet in infile.readlines():
        if re.search(r'#',tweet):
            timeinfo = [tweet.split("\t")[date_column],tweet.split("\t")[time_column]]
            tweet_datetime = time_functions.return_datetime(timeinfo[0],time=timeinfo[1],setting="vs")
            for hashtag in re.findall(r' ?(#[^ \n]+) ?',tweet):
                hashtag = hashtag.lower()
                hashtag_time[hashtag][tweet_datetime] += 1
                hashtag_frequency[hashtag] += 1
    infile.close()

#cluster similar hashtags
hashtags = hashtag_frequency.keys()
sim_hashtags = []
for hashtag1 in hashtags:
    for hashtag2 in hasthags:
        print hashtag1,hashtag2,levenshtein(hashtag1,hashtag2)

exit()
# prune hashtags occuring less then 10 times
for h in sorted(hashtag_frequency, key=hashtag_frequency.get, reverse=True)[:250]:
    print h, hashtag_frequency[h]


# for each set of 1000 hashtags in frequency list
# count the number of occurrences per hour
# write hour-frequency lists to file 
