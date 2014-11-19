#!/usr/bin/env python

from __future__ import division
import argparse
import codecs
import multiprocessing
from collections import defaultdict
import numpy
from scipy.stats import poisson
import gen_functions
import datetime
from operator import itemgetter
import re

import gen_functions

"""
"""
parser = argparse.ArgumentParser(description = "")
parser.add_argument('-i', action = 'store', required = True, help = "the input file")  
parser.add_argument('-w', action = 'store', required = True, help = "the output file")
parser.add_argument('-s', action = 'store', type = int, default = 24, help = "the size of the sliding window (in the amount of hours; default = 24)")
parser.add_argument('-b', action = 'store', type = int, nargs='+', help = "the begin date time")
parser.add_argument('-u', action = 'store', default = "day", help = "the unit of time windows")
parser.add_argument('--jobs', action = 'store', type = int, default = 1, help = "specify the number of parralel jobs")

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

def make_windows(lines,queue):
    for line in lines:
        tokens = line.strip().split("\t")
        term = tokens[0]
        output = [term,[]]
        vals = tokens[1].split("|")
        if args.s == 1:
            output[1] = [int(x) for x in vals]
        else:
            i = 0
            while i < len(vals):
                output[1].append(sum([int(x) for x in vals[i:i+args.s]])) 
                i += args.s
        queue.put(output)

def retrieve_states_hmm(sequences,queue):
    for sequence in sequences:
        print sequence
        s = sequence[1]
        print s
        mean = numpy.mean(s)
        st_dev = gen_functions.return_standard_deviation(s)
        po = [poisson(mean),poisson(mean*3)]    
        optimal_state = [[po[0].pmf(s[0]),[0]],[po[1].pmf(s[0]),[1]],0]
        for i,interval in enumerate(s[1:]):
            print interval
            optimal_state_new = [[],[],optimal_state[2]]
            bconfs = []
            for state in [0,1]:
                opts = []
                observed = po[state].pmf(interval)
                print observed
                opts = [(optimal_state[statem1][0]*p[statem1][state]*observed) for statem1 in [0,1]]
                quit()
                best = opts.index(max(opts))
                optimal_state_new[state].append(max(opts))
                optimal_state_new[state].append(optimal_state[best][1] + [state])
            bconf = (interval - mean) - (2*st_dev)       
            if bconf > optimal_state_new[2]:
                optimal_state_new[2] = bconf
                optimal_state_new[3] = interval
            optimal_state = optimal_state_new
        pathprobs = [optimal_state[0][0],optimal_state[1][0]]
        top_path_index = pathprobs.index(max(pathprobs))
        queue.put([sequence[0],optimal_state[top_path_index][1],optimal_state[2],optimal_state[3]])

print "making sliding windows"

lines = inread.readlines()
inread.close()
print len(lines),"lines"
q = multiprocessing.Queue()        
chunks = gen_functions.make_chunks(lines,args.jobs)
for chunk in chunks:
    p = multiprocessing.Process(target=make_windows,args=[chunk,q])
    p.start()

sliding_windows = []
while True:
    l = q.get()
    sliding_windows.append(l)
    print len(sliding_windows),"of",len(lines),"windows"
    if len(sliding_windows) == len(lines):
        break

print "calculating burstiness"
q = multiprocessing.Queue()        
chunks = gen_functions.make_chunks(sliding_windows,args.jobs)
for chunk in chunks:
    p = multiprocessing.Process(target=retrieve_states_hmm,args=[chunk,q])
    p.start()

states = []
while True:
    l = q.get()
    states.append(l)
    print len(states),"of",len(lines),"states"
    print l
    if 1 in l[1]:
        dates = []
        for i,u in enumerate(l[1]):
            if u == 1:
                if args.u == "day":
                    dates.append(begin_d+datetime.timedelta(days=i*args.s))
                elif args.u == "hour":
                    dates.append(begin_d+datetime.timedelta(hours=i*args.s))
                elif args.u == "minute":
                    dates.append(begin_d+datetime.timedelta(minutes=i*args.s))
        #output term\tburstiness\tfrequency\tdays
        outwrite.write("\t".join([l[0],str(l[2]),str(l[3])," ".join([str(d) for d in dates])]) + "\n")
    if len(states) == len(lines):
        break

outwrite.close()
