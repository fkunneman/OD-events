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
begin_date = datetime.date(2013,6,22)
term_windows = defaultdict(list)
term_burst = defaultdict(list)
p = defaultdict(lambda : {}) 
p[0][0] = 0.9
p[1][1] = 0.6
p[0][1] = 0.1
p[1][0] = 0.4

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
    #m = [mean,mean*3]
    po = [poisson(mean),poisson(mean*3)]    
    optimal_state = [[po[0].pmf(sequence[0]),[0]],[po[1].pmf(sequence[0]),[1]]]
    print optimal_state
    for i,interval in enumerate(sequence[1:]):
        optimal_state_new = [[],[]]
        for state in [0,1]:
            opts = []
            observed = po[state].pmf(interval)
            opts = [(optimal_state[statem1][0]*p[statem1][state]*observed) for statem1 in [0,1]]
            best = opts.index(max(opts))
            optimal_state_new[state].append(max(opts))
            optimal_state_new[state].append(optimal_state[best][1] + [state])
        optimal_state = optimal_state_new
        print i,optimal_state





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
    #print bursts,sorted(bursts,reverse=True)[:5]
    term_burst[term] = sorted(bursts,reverse=True)[:5]

ranked_terms = sorted(term_burst.items(), key=lambda x:x[1][0],reverse=True)

#sorted(term_burst.items(), key=lambda e: e[0][0])
for term,value in ranked_terms:    
    outwrite.write(term + "\t")
    for v in value:
        outwrite.write(" ".join([str(x) for x in v]) + "|")
    outwrite.write("\n")
