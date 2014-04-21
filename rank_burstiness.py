#!/usr/bin/env python

from __future__ import division
import argparse
import codecs
from collections import defaultdict
import numpy
import gen_functions
import datetime

"""
"""
parser = argparse.ArgumentParser(description = "")
parser.add_argument('-i', action = 'store', required = True, help = "the input file")  
parser.add_argument('-w', action = 'store', required = True, help = "the output file")
parser.add_argument('-m', action = 'store', choices = ["minus","divide"], help = "the burstiness metric (choose between \'minus\' and \'divide\'"))
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

print "making sliding windows"

for line in inread.readlines():
    tokens = line.strip().split("\t")
    term = tokens[0]
    vals = tokens[1].split("|")
    term_windows[term] = [vals[x:x+args.s] for x in xrange(1, len(vals), 24)]
    print vals, [vals[x:x+args.s] for x in xrange(1, len(vals), 24)]

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
        outwrite.write(" ".join(v) + "|")
    outwrite.write("\n")



