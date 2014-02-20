#! /usr/bin/env python

#testcomment

from __future__ import division
import sys
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
        if retweet_removal and re.search(r'( |^)RT ?',tweet.split("\t")[-1]):
            continue
        if re.search(r'#',tweet):
            timeinfo = [tweet.split("\t")[date_column],tweet.split("\t")[time_column]]
            tweet_date = time_functions.return_datetime(timeinfo[0],time = timeinfo[1],minute = True,setting="vs")
            for hashtag in re.findall(r' ?(#[^ \n]+) ?',tweet):
                # if re.search(r'\s',hashtag):
                #     print hashtag,tweet
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
start_datetime = time_functions.return_datetime(start_timeinfo[0],time = start_timeinfo[1],minute = True,setting="vs")
end_tweet = gzip.open(infiles[-1],"rb").readlines()[-1]
end_timeinfo = [end_tweet.split("\t")[date_column],end_tweet.split("\t")[time_column]]
end_datetime = time_functions.return_datetime(end_timeinfo[0],time = end_timeinfo[1],minute = True,setting="vs")
timesegments = [start_datetime]
current_time = start_datetime
while current_time <= end_datetime:
    current_time += datetime.timedelta(hours=1)
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
hashtag_peakscore_stripped = []
for h in hashtags[:freq_bound]:
    sequence = []
    sequence_stripped = []
    hashtag_hours = sorted(hashtag_time[h].keys())
    for hour in timesegments:
        if hour in hashtag_hours:
            sequence.append(hashtag_time[h][hour])
        else:
            sequence.append(0)
    for hour in hashtag_hours:
        sequence_stripped.append(hashtag_time[h][hour])
    print sequence,sequence_stripped
    mas = max(sequence_stripped)
    medians = numpy.median(sequence_stripped)
    means = numpy.mean(sequence_stripped)
    score1s = mas/medians
    score2s = mas/means
    peaktime = sequence_stripped.index(mas)
    left = 1
    t = peaktime
    while left > 0.1:
        t -= 1
        if t < 0:
            break
        left = sequence_stripped[t] / mas
    score3s = peaktime - t
    hashtag_peakscore_stripped.append((h,score1s,score2s,score3s,"|".join([str(e) for e in sequence]),mas,medians))
    ma = max(sequence)
    median = numpy.median(sequence) + 1
    mean = numpy.mean(sequence)
    st = gen_functions.return_standard_deviation(sequence)
    score1 = ma/median
    score2 = ma/mean
    peaktime = sequence.index(ma)
    left = 1
    t = peaktime
    while left > 0.1:
        t -= 1
        if t < 0:
            break
        left = sequence[t] / ma
    score3 = peaktime - t
    hashtag_peakscore.append((h,score1,score2,score3,st,"|".join([str(e) for e in sequence]),ma,median))

outfile1 = open(outfile_frame + "median.txt","w")
for y in sorted(hashtag_peakscore,key=lambda x: x[1],reverse=True):
    yl = [str(z) for z in y] 
    outfile1.write(" ".join(yl) + "\n")
outfile1.close()

outfile2 = open(outfile_frame + "mean.txt","w")
for y in sorted(hashtag_peakscore,key=lambda x: x[2],reverse=True):
    yl = [str(z) for z in y]
    outfile2.write(" ".join(yl) + "\n")
outfile2.close()

outfile3 = open(outfile_frame + "stdev.txt","w")
for y in sorted(hashtag_peakscore,key=lambda x: x[4],reverse=True):
    yl = [str(z) for z in y]
    outfile3.write(" ".join(yl) + "\n")
outfile3.close()

outfile4 = open(outfile_frame + "median_stripped.txt","w")
for y in sorted(hashtag_peakscore_stripped,key=lambda x: x[1],reverse=True):
    yl = [str(z) for z in y]
    outfile4.write(" ".join(yl) + "\n")
outfile4.close()

outfile5 = open(outfile_frame + "mean_stripped.txt","w")
for y in sorted(hashtag_peakscore_stripped,key=lambda x: x[2],reverse=True):
    yl = [str(z) for z in y]
    outfile5.write(" ".join(yl) + "\n")
outfile5.close()

outfile6 = open(outfile_frame + "leftcontext.txt","w")
for y in sorted(hashtag_peakscore,key=operator.itemgetter(1,3),reverse=True):
    yl = [str(z) for z in y]
    outfile6.write(" ".join(yl) + "\n")
outfile6.close()

outfile7 = open(outfile_frame + "leftcontext_stripped.txt","w")
for y in sorted(hashtag_peakscore_stripped,key=operator.itemgetter(1,3),reverse=True):
    yl = [str(z) for z in y]
    outfile7.write(" ".join(yl) + "\n")
outfile7.close()

# outfile8 = open(outfile_frame + "leftcontext_meanr_stripped.txt","w")
# for y in sorted(hashtag_peakscore_stripped,key=lambda x: x[2],reverse=True):
#     yl = [str(z) for z in y]
#     outfile8.write(" ".join(yl) + "\n")
# outfile8.close()

# outfile9 = open(outfile_frame + "leftcontext_meanr.txt","w")
# for y in sorted(hashtag_peakscore_stripped,key=lambda x: x[2],reverse=True):
#     yl = [str(z) for z in y]
#     outfile9.write(" ".join(yl) + "\n")
# outfile9.close()

# for each set of 1000 hashtags in frequency list
# count the number of occurrences per hour
# write hour-frequency lists to file 
