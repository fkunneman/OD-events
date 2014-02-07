#! /usr/bin/env python

import sys
import datetime
from collections import defaultdict
import gzip
import re

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
                hashtag_time[hashtag][tweet_datetime] += 1
                hashtag_frequency[hashtag] += 1
    print hashtag_frequency
    infile.close()




#cluster similar hashtags

# prune hashtags occuring less then 10 times

# for each set of 1000 hashtags in frequency list
# count the number of occurrences per hour
# write hour-frequency lists to file 
