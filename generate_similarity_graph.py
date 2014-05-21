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
# parser.add_argument('-b', action = 'store', required = True, help = "the file with bursty unigrams")
# parser.add_argument('-t', action = 'store', required = True, help = "the file with term frequencies over time")
# parser.add_argument('-o', action = 'store', required = True, help = "the file to write the per-date similarity graph to")

args = parser.parse_args()

#cluster files by date
date = re.compile(r"(\d{4})(\d{2})(\d{2})-")
date_files = defaultdict(list)
for f in args.i:
    dates = date.search(f).groups()
    print dates





#make date-term-graph



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

