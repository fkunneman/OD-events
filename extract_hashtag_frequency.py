#! /usr/bin/env python

import sys
import datetime
from collections import defaultdict
import gzip
import re
import numpy
from pynlpl.statistics import levenshtein

import time_functions

outfile = open(sys.argv[1],"w")
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
            tweet_date = time_functions.return_datetime(timeinfo[0],setting="vs")
            for hashtag in re.findall(r' ?(#[^ \n]+) ?',tweet):
                hashtag = hashtag.lower()
                hashtag_time[hashtag][tweet_date] += 1
                hashtag_frequency[hashtag] += 1
    infile.close()

#cluster similar hashtags
# hashtags = hashtag_frequency.keys()
# sim_hashtags = []
# for hashtag1 in hashtags:
#     print hashtag1
#     for hashtag2 in hashtags:
#         dist = levenshtein(hashtag1,hashtag2)
#         if dist <= 2:
#             print hashtag1,hashtag2,levenshtein(hashtag1,hashtag2)

hashtags = sorted(hashtag_frequency, key=hashtag_frequency.get, reverse=True)
# prune hashtags occuring less then 10 times
for i,h in enumerate(hashtags):
    if hashtag_frequency[h] == 10:
        freq_bound = i
        break

# make hashtag time sequences
# start_tweet = gzip.open(infiles[0],"rb").readlines()[0]
# start_timeinfo = [start_tweet.split("\t")[date_column],start_tweet.split("\t")[time_column]]
# start_datetime = time_functions.return_datetime(start_timeinfo[0],time=start_timeinfo[1],setting="vs")
# end_tweet = gzip.open(infiles[-1],"rb").readlines()[-1]
# end_timeinfo = [end_tweet.split("\t")[date_column],end_tweet.split("\t")[time_column]]
# end_datetime = time_functions.return_datetime(end_timeinfo[0],time=end_timeinfo[1],setting="vs")
# timesegments = []
# current_time = start_datetime
# while current_time <= end_datetime:
#     current_time += datetime.timedelta(days=1)
#     timesegments.append(current_time) 
# print timesegments

# hashtag_sequence = defaultdict(list)
# for h in hashtags[:10]:
#     timepoints = hashtag_time[h]
#     i = 0
#     hashtag_sequence[h] = [0] * len(timesegments)
#     for j,ts in enumerate(timesegments):
#         while timepoints[i] < ts:
#             hashtag_sequence[h][j] += 1
#             i += 1
#             if i == len(timepoints):
#                 break
#     print h,hashtag_sequence[h]

hashtag_peakscore = []
for h in hashtags[:freq_bound]:
    sequence = [hashtag_time[h][d] for d in sorted(hashtag_time[h].keys())]
    ma = max(sequence)
    median = numpy.median(sequence)
    score = ma/median
    hashtag_peakscore.append((h,str(score),"|".join([str(e) for e in sequence]),str(ma),str(median))

for y in sorted(hashtag_peakscore,key=lambda x: x[1],reverse=True):
     outfile.write(" ".join(y))
outfile.close()
# for each set of 1000 hashtags in frequency list
# count the number of occurrences per hour
# write hour-frequency lists to file 
