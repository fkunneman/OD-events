#!/usr/bin/env python

from __future__ import division
import argparse
import codecs
import re
from collections import defaultdict
import datetime
import math

"""
Script to calculate the bursty weight of word frequencies
"""
parser = argparse.ArgumentParser(description = "Script to calculate the bursty weight from word frequencies")
parser.add_argument('-w', action = 'store', required = True, help = "The file with the word frequencies")  
parser.add_argument('-b', action = 'store', required = True, help = "the file with bursty terms")
parser.add_argument('-t', action = 'store', nargs = '+', required = True, help = "the files with tweets")
parser.add_argument('-o', action = 'store', required = True, help = "the output directory for the bursty weight per term")

args = parser.parse_args()

date_num_tweets = []
date_files = defaultdict(list)
date_burst = defaultdict(list)
term_Ps = defaultdict(list)


def sigmoid(x):
    return 1 / (1 + math.exp(-x))

#cluster files by date
date = re.compile(r"(\d{4})(\d{2})(\d{2})-")
for f in args.t:
    dates = date.search(f).groups()
    date_files[datetime.date(int(dates[0]),int(dates[1]),int(dates[2]))].append(f)
#count num_tweets per date
for i,date in enumerate(sorted(date_files.keys())):
    #collect tweets
    tweets = []
    for f in date_files[date]:
        infile = codecs.open(f,"r","utf-8")
        tweets.extend([l.strip() for l in infile.readlines()])
        infile.close()
    Nt = len(tweets)
    date_num_tweets.append(Nt)

#load in bursty terms 
print "loading in bursty terms"
burstyfile = codecs.open(args.b,"r","utf-8")
bursties = []
for line in burstyfile.readlines():
    tokens = line.strip().split("\t")
    for dateunit in tokens[2].split(" "):
        datestring = [int(x) for x in dateunit.split("/")]
        date_burst[datetime.date((datestring[0]+2000),datestring[1],datestring[2])].append(tokens[0])
    bursties.append(tokens[0])
burstyfile.close()
bursties_set = set(bursties)

print "loading in word frequencies"
#load in word frequency file
term_windows = defaultdict(list)
infile = codecs.open(args.w,"r","utf-8")
for line in infile.readlines():
    tokens = line.strip().split("\t")
    term = tokens[0]
    if bool(set([term]) & set(bursties_set)):
        vals = tokens[1].split("|")
        i = 0
        while i < len(vals):
            term_windows[term].append(sum([int(x) for x in vals[i:i+24]])) 
            i += 24

print "dates",len(date_num_tweets),"windows",len(term_windows[term_windows.keys()[0]]),"bursties",len(date_burst.keys())

for term in bursties:
    windows = term_windows[term]
    L = len([x for x in term_windows[term] if x > 0])
    vals = []
    for i,window in enumerate(windows):
        if window > 0:
            Fst = window # f_u,t
            Nt = date_num_tweets[i]
            vals.append(Fst/Nt)
    Ps = sum(vals) / len(vals) # similar to 1/l * sum(vals)
    #print term,vals,Fst,Nt,Ps
    term_Ps[term] = Ps

for i,date in enumerate(sorted(date_burst.keys())):
    outfile = codecs.open(args.o + str(date) + ".txt","w","utf-8")
    Nt = date_num_tweets[i]
    for term in date_burst[date]:
        Ps = term_Ps[term]
        Est = Ps * Nt
        stdev_Est = math.sqrt(Est * (1-Ps))
        Pbst = sigmoid(10 * ((term_windows[term][i] - (Est + stdev_Est)) / (stdev_Est)))
        print term,"Est",Est,"Ps",Ps,"Nt",Nt,"stdev_Est",stdev_Est,"Pbst",Pbst
        outfile.write(term + "\t" + str(Pbst) + "\n")
