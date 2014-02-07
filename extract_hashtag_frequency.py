#! /usr/bin/env python

import sys
import datetime
from collections import defaultdict
import gzip

import time_functions

outfile = sys.argv[1]
date_column = int(sys.argv[2])
time_column = int(sys.argv[3])
infiles = sys.argv[4:]

file_hour = {}
#order files in time
print "Ordering files in time..."
for f in infiles:
    print f
    if f[-2:] == "gz":
        infile = gzip.open(f,"rb")
    else:
        infile = open(f)
    tweet = infile.readlines()[100]
    #print tweet
    timeinfo = [tweet.split("\t")[date_column],tweet.split("\t")[time_column]]
    #print timeinfo
    tweet_datetime = time_functions.return_datetime(timeinfo[0],time=timeinfo[1],setting="vs")
    print tweet_datetime
    file_hour[tweet_datetime] = f
    infile.close()

# make hashtag frequency list
# for each hour
for hour in sorted(file_hour.keys()):
    f = file_hour[hour]
    if f[-2:] == "gz":
        infile = gzip.open(f,"rb")
    else:
        infile = open(f)
    # for each tweet

# add hashtag to counter

#cluster similar hashtags

# prune hashtags occuring less then 10 times

# for each set of 1000 hashtags in frequency list
# count the number of occurences per hour
# write hour-frequency lists to file 
