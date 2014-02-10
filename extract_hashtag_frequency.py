#! /usr/bin/env python

import sys
import datetime
from collections import defaultdict
import gzip
import re
import numpy
from pynlpl.statistics import levenshtein

import time_functions

outfile1 = open(sys.argv[1],"w")
outfile2 = open(sys.argv[2],"w")
date_column = int(sys.argv[3])
time_column = int(sys.argv[4])
infiles = sys.argv[5:]

# make hashtag frequency list
hashtag_frequency = defaultdict(int)
hashtag_time = defaultdict(lambda : defaultdict(int))
for f in infiles:
    #print f
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
                if re.search(' ',hashtag):
                    print hashtag,tweet
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
start_tweet = gzip.open(infiles[0],"rb").readlines()[0]
start_timeinfo = [start_tweet.split("\t")[date_column],start_tweet.split("\t")[time_column]]
start_datetime = time_functions.return_datetime(start_timeinfo[0],setting="vs")
end_tweet = gzip.open(infiles[-1],"rb").readlines()[-1]
end_timeinfo = [end_tweet.split("\t")[date_column],end_tweet.split("\t")[time_column]]
end_datetime = time_functions.return_datetime(end_timeinfo[0],setting="vs")
timesegments = [start_datetime]
current_time = start_datetime
while current_time <= end_datetime:
    current_time += datetime.timedelta(days=1)
    timesegments.append(current_time) 

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
    sequence = []
    hashtag_days = sorted(hashtag_time[h].keys())
    for day in timesegments:
        if day in hashtag_days:
            sequence.append(hashtag_time[h][day])
        else:
            sequence.append(0)
    ma = max(sequence)
    median = numpy.median(sequence) + 1
    mean = numpy.mean(sequence)
    score1 = ma/median
    score2 = ma/mean
    hashtag_peakscore.append((h,str(score1),str(score2),"|".join([str(e) for e in sequence]),str(ma),str(median)))

for y in sorted(hashtag_peakscore,key=lambda x: x[1],reverse=True):
     outfile1.write(" ".join(y) + "\n")
outfile1.close()

for y in sorted(hashtag_peakscore,key=lambda x: x[2],reverse=True):
     outfile2.write(" ".join(y) + "\n")
outfile2.close()

# for each set of 1000 hashtags in frequency list
# count the number of occurrences per hour
# write hour-frequency lists to file 
