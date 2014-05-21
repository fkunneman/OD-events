#!/usr/bin/env python

import argparse
import codecs
from collections import defaultdict
import datetime
import re

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

date_files = defaultdict(list)
date_burstyterms = defaultdict(list)

#cluster files by date
date = re.compile(r"(\d{4})(\d{2})(\d{2})-")
for f in args.i:
    dates = date.search(f).groups()
    date_files[datetime.date(int(dates[0]),int(dates[1]),int(dates[2]))].append(f)

#make date-term-graph
burstyfile = codecs.open(args.b,"r","utf-8")
date = re.compile(r"(\d{2})/(\d{2})/(\d{2})")
for line in burstyfile:
    tokens = line.strip().split("\t")
    dates = tokens[2].split(" ")
    for t in dates:
        d = date.search(t).groups()
        print datetime.date(int("20" + d[0]),int(d[1]),int(d[2]),tokens[0]
        date_burstyterms[datetime.date(int("20" + d[0]),int(d[1]),int(d[2]))].append(tokens[0])




#for each date

#extract all tweets
#make vocabulary

#make term-tweet vectors
        #extract tweets containing term
        #generate vector

#generate combinations of vectors
#for each combination:
    #compute similarity


#extract term sub-window freq

