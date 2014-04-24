#!/usr/bin/env python

from __future__ import division
import argparse
import codecs
from collections import defaultdict
import numpy
from scipy.stats import poisson
import gen_functions
import datetime


"""
"""
parser = argparse.ArgumentParser(description = "")
parser.add_argument('-i', action = 'store', required = True, help = "the input file")  
parser.add_argument('-w', action = 'store', required = True, help = "the output file")
parser.add_argument('-m', action = 'store', choices = ["minus","divide","hmm"], help = "the burstiness metric (choose between \'minus\' and \'divide\'")
parser.add_argument('-s', action = 'store', type = int, default = 24, help = "the size of the sliding window (in the amount of hours; default = 24)")

args = parser.parse_args()

inread = codecs.open(args.i,"r","utf-8")
outwrite = codecs.open(args.w,"w","utf-8")
begin_date = datetime.datetime(2013,6,22,0,0,0)
term_windows = defaultdict(list)
term_burst = defaultdict(list)

def calculate_burstiness(hist,freq,metric):
    mean = numpy.mean(hist)
    st_dev = gen_functions.return_standard_deviation(hist)
    if metric == "minus":
        return (freq-mean-(2*st_dev))
    elif metric == "divide":
        return ((freq-mean)/st_dev)

def retrieve_states_hmm(sequence):
    #calculate mean
    mean = numpy.mean(sequence)
    m0 = mean
    m1 = mean*3
    p00 = 0.9
    p11 = 0.6
    p01 = 0.1
    p10 = 0.4
    p0 = poisson(m0)
    p1 = poisson(m1)
    optimal_state()
    for interval in sequence:



print "making sliding windows"

for line in inread.readlines():
    tokens = line.strip().split("\t")
    term = tokens[0]
    vals = tokens[1].split("|")
    i = 0
    while i < len(vals):
        term_windows[term].append(sum([int(x) for x in vals[i:i+args.s]])) 
        i += args.s
    #print vals, term_windows[term]

print "calculating burstiness"
for term in term_windows.keys():
    bursts = []
    for i,interval in enumerate(term_windows[term][3:]):
        h = term_windows[term][0:i+3]
        bursts.append((calculate_burstiness(h,interval,args.m),begin_date+datetime.timedelta(days=i+3)))
    term_burst[term] = sorted(bursts)[:5]

ranked_terms = sorted(term_burst.items(), key=lambda e: e[0][0])
for term,value in ranked_terms:
    outwrite.write(term + "\t")
    for v in value:
        outwrite.write(" ".join([str(x) for x in v]) + "|")
    outwrite.write("\n")
