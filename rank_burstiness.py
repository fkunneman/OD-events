#!/usr/bin/env python

from __future__ import division
import argparse
import codecs
from collections import defaultdict
import numpy
from scipy.stats import poisson
import gen_functions
import datetime
from operator import itemgetter
import re

"""
"""
parser = argparse.ArgumentParser(description = "")
parser.add_argument('-i', action = 'store', required = True, help = "the input file")  
parser.add_argument('-w', action = 'store', required = True, help = "the output file")
parser.add_argument('-m', action = 'store', choices = ["minus","divide","hmm"], help = "the burstiness metric")
parser.add_argument('-s', action = 'store', type = int, default = 24, help = "the size of the sliding window (in the amount of hours; default = 24)")
parser.add_argument('-b', action = 'store', type = int, nargs='+', help = "the begin date time")
parser.add_argument('-u', action = 'store', default = "day", help = "the unit of time windows")

args = parser.parse_args()

inread = codecs.open(args.i,"r","utf-8")
outwrite = codecs.open(args.w,"w","utf-8")
begin_d = datetime.datetime(args.b[0],args.b[1],args.b[2],args.b[3],args.b[4],args.b[5])
term_windows = defaultdict(list)
term_burst = []
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
    st_dev = gen_functions.return_standard_deviation(sequence)
    print mean, st_dev
    #m = [mean,mean*3]
    po = [poisson(mean),poisson(mean*3)]    
    optimal_state = [[po[0].pmf(sequence[0]),[0]],[po[1].pmf(sequence[0]),[1]],0]
    for i,interval in enumerate(sequence[1:]):
        optimal_state_new = [[],[],optimal_state[2]]
        bconfs = []
        for state in [0,1]:
            opts = []
            observed = po[state].pmf(interval)
            opts = [(optimal_state[statem1][0]*p[statem1][state]*observed) for statem1 in [0,1]]
            best = opts.index(max(opts))
            optimal_state_new[state].append(max(opts))
            optimal_state_new[state].append(optimal_state[best][1] + [state])
        bconf = (interval - mean) - (2*st_dev)       
        if bconf > optimal_state_new[2]:
            optimal_state_new[2] = bconf
        optimal_state = optimal_state_new
    pathprobs = [optimal_state[0][0],optimal_state[1][0]]
    top_path_index = pathprobs.index(max(pathprobs))
    print [optimal_state[top_path_index][1],optimal_state[2]] 
    return [optimal_state[top_path_index][1],optimal_state[2]]

print "making sliding windows"

for line in inread.readlines():
    tokens = line.strip().split("\t")
    term = tokens[0]
#    if not re.search("^@",term):
    vals = tokens[1].split("|")
    i = 0
    while i < len(vals):
        term_windows[term].append(sum([int(x) for x in vals[i:i+args.s]])) 
        i += args.s
    #print vals, term_windows[term]

print "calculating burstiness"
for term in term_windows.keys():
    print term,term_windows[term]
    if args.m == "hmm":
        path = retrieve_states_hmm(term_windows[term])
#        print term,path
        if 1 in path[0]:
            term_burst.append([term] + path)

#sort terms according to burstiness
term_burst_sorted = sorted(term_burst, key=itemgetter(2,0,1),reverse=True)

#print term_burst_sorted
#for each term
for term in term_burst_sorted:
    #retrieve day/days
    dates = []
    for i,u in enumerate(term[1]):
        if u == 1:
            if args.u == "day":
                dates.append(begin_d+datetime.timedelta(days=i*args.s))
            elif args.u == "hour":
                dates.append(begin_d+datetime.timedelta(hours=i*args.s))
            elif args.u == "minute":
                dates.append(begin_d+datetime.timedelta(minutes=i*args.s))
    #output term\tburstiness\tdays
    outwrite.write("\t".join([term[0],str(term[2])," ".join([d.strftime('%y/%m/%d %h:%m') for d in dates])]) + "\n")


    # bursts = []
    # for i,interval in enumerate(term_windows[term][3:]):
    #     h = term_windows[term][0:i+3]
    #     bursts.append((calculate_burstiness(h,interval,args.m),begin_date+datetime.timedelta(days=i+3)))
    # term_burst[term] = sorted(bursts)[:5]

# ranked_terms = sorted(term_burst.items(), key=lambda e: e[0][0])
# for term,value in ranked_terms:
#     outwrite.write(term + "\t")
#     for v in value:
#         outwrite.write(" ".join([str(x) for x in v]) + "|")
#     outwrite.write("\n")
