#!/usr/bin/env python

from __future__ import division
import argparse
import codecs
from collections import defaultdict
import datetime
import re
import multiprocessing
import numpy
from sklearn.metrics import pairwise_distances
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from itertools import combinations

import gen_functions

"""
Script to generate similarity graphs of bursty features
"""
parser = argparse.ArgumentParser(description = "Script to generate similarity graphs of bursty features")  
parser.add_argument('-b', action = 'store', required = True, help = "the file with bursty unigrams")
parser.add_argument('-t', action = 'store', required = True, help = "the file with term frequencies over time")
parser.add_argument('-a', action = 'store', choices = ['twevent','tags'], default = 'twevent', help = "choose the similarity metric")
parser.add_argument('-i', action = 'store', nargs='+',required = False, help = "The files with tweets per hour (only needed for \'twevent\' metric)")
parser.add_argument('-d', action = 'store', required = False, help = "the file with co-occuring term frequencies over time (only needed for \'tags\'' metric)")
parser.add_argument('-o', action = 'store', required = True, help = "the directory to write similarity files to")

args = parser.parse_args()

date_burstyterms = defaultdict(list)
date_seqs = defaultdict(lambda : defaultdict(list))

def count_terms(lines,queue):
    term_frequency = defaultdict(int)
    for line in lines:
        for term in line.split(" "):
            term_frequency[term] += 1
    queue.put(term_frequency)

def extract_tweets(tweets,terms,queue):
    appended_docs = defaultdict(list)
#    for term in terms:
#        standard_vectors[term] = [0] * len(tind.keys())
    termss = set(terms)
    for tweet in tweets:
        words = list(set(tweet.split(" ")))
        if bool(set(words) & termss):
            for term in terms:
                if term in words:
                    appended_docs[term].extend(words)
                    # for word in words:
                    #     if tboo[word]:
                    #         standard_vectors[term][tind[word]] += 1
    queue.put(appended_docs)

def score_tagsim(cs,csegs):
    tsims = defaultdict(lambda : defaultdict(float))
    for i,c in enumerate(cs):
        print "cooc burstscore",i,"of",len(combis)
        cooc = sorted(c)
        seq = [x for x in cseqs[cooc[0]][cooc[1]] if x > 0]
        if len(seq) > 0:
            freq = sum(cooc_seqs[cooc[0]][cooc[1]][seqstart:seqend])
            if freq > 0:
                mean = sum(seq)/len(seq)
                st_dev = gen_functions.return_standard_deviation(seq)
                burstscore_coocs = freq-mean-(2*st_dev)
            #cooc_freq[cooc[0]][cooc[1]] = freq
                term_sims[cooc[0]][cooc[1]] = burstscore_coocs + (burstscore_terms[cooc[0]]*freq) + (burstscore_terms[cooc[1]]*freq)
                print cooc[0],cooc[1],"a",burstscore_coocs,"b1",burstscore_terms[cooc[0]],"b2",freq,"c1",burstscore_terms[cooc[1]],"c2",freq,"sim",burstscore_coocs + (burstscore_terms[cooc[0]]*freq) + (burstscore_terms[cooc[1]]*freq)
            else:
                term_sims[cooc[0]][cooc[1]] = 0
        else:
            term_sims[cooc[0]][cooc[1]] = 0
    return tsims

#make date-burstyterm-graph
burstyfile = codecs.open(args.b,"r","utf-8")
bursties = []
date = re.compile(r"(\d{2})/(\d{2})/(\d{2})")
for line in burstyfile:
    tokens = line.strip().split("\t")
    bursties.append(tokens[0])
    dates = tokens[2].split(" ")
    for t in dates:
        d = date.search(t).groups()
        date_burstyterms[datetime.date(int("20" + d[0]),int(d[1]),int(d[2]))].append(tokens[0])
burstyfile.close()

#make term_sequence-graph
term_seqs = defaultdict(list)
seqfile = codecs.open(args.t,"r","utf-8")
for line in seqfile.readlines():
    tokens = line.strip().split("\t") 
    term_seqs[tokens[0]] = [int(x) for x in tokens[1].split("|")]
seqfile.close()

if args.a == "twevent":
    date_files = defaultdict(list)
    #cluster files by date
    date = re.compile(r"(\d{4})(\d{2})(\d{2})-")
    for f in args.i:
        dates = date.search(f).groups()
        date_files[datetime.date(int(dates[0]),int(dates[1]),int(dates[2]))].append(f)

if args.a == "tags":
    #make co-oc_term_sequence_graph
    cooc_seqs = defaultdict(lambda : defaultdict(list))
    seqfile = codecs.open(args.d,"r","utf-8")
    for line in seqfile.readlines():
        tokens = line.strip().split("\t") 
        terms = sorted(tokens[0].split(" "))
        cooc_seqs[terms[0]][terms[1]] = [int(x) for x in tokens[1].split("|")]
    seqfile.close()

#for each date
for j,date in enumerate(sorted(date_burstyterms.keys())):
    term_sims = defaultdict(lambda : defaultdict(float))
    burstyterms = date_burstyterms[date]
    print date,"num terms:",len(burstyterms)

    if args.a == "twevent":
        bursty_seqs = defaultdict(list)
        seqstart = j*24
        seqend = seqstart+24
        for bt in burstyterms:
            bursty_seqs[bt] = term_seqs[bt][seqstart:seqend]
        for s in range(0,24,2):
            bt_weight = {}
            #calculate weight for each bursty term
            for bt in burstyterms:
                win = bursty_seqs[bt]
                subwin = [win[s],win[s+1]]
                try:
                    bt_weight[bt] = sum(subwin)/sum(win)
                except ZeroDivisionError:
                    bt_weight[bt] = 0.0

            #calculate similarity between bursty terms
            tweets = []
            #extract all tweets
            files = [date_files[date][s],date_files[date][s+1]]
            for f in files:
                print f
                infile = codecs.open(f,"r","utf-8")
                tweets.extend([l.strip() for l in infile.readlines()])
                infile.close()

            #make vocabulary
            print "making vocabulary"
            q = multiprocessing.Queue()
            tweet_chunks = gen_functions.make_chunks(tweets,dist=True)
            for i in range(len(tweet_chunks)):
                p = multiprocessing.Process(target=count_terms,args=[tweet_chunks[i],q])
                p.start()

            ds = []
            while True:
                l = q.get()
                ds.append(l)
                if len(ds) == len(tweet_chunks):
                    break
            term_frequency = defaultdict(int)
            for d in ds:
                for k in d:
                    term_frequency[k] += d[k]
            term_index = {}
            # term_b = {}
            i = 0
            for term in term_frequency.keys():
                if term_frequency[term] > 1:
                    term_index[term] = i
                    # term_b[term] = True
                    i += 1
                # else:
                #     term_b[term] = False

            #make burstyterm-tweet vectors
            print "making pseudo-docs"    
            #extract tweets containing term and generate vector
            q = multiprocessing.Queue()
            term_chunks = gen_functions.make_chunks(burstyterms,dist=True)
            for i in range(len(term_chunks)):
                p = multiprocessing.Process(target=extract_tweets,args=[tweets,term_chunks[i],q])
                p.start()

            ds = []
            while True:
                l = q.get()
                ds.append(l)
                if len(ds) == len(term_chunks):
                    break
            pseudodocs = []
            index_term = {}
            y = 0
            for d in ds:
                for k in d:
                    index_term[k] = y
                    y += 1
                    pseudodocs.append((k," ".join(d[k])))
            print pseudodocs
            #compute similarities
            print "calculating similarities"
            tfidf_vectorizer = TfidfVectorizer()
            tfidf_matrix = tfidf_vectorizer.fit_transform([x[1] for x in pseudodocs])
            cosim = cosine_similarity(tfidf_matrix, tfidf_matrix)
            print "calculating feature-pair subwindow-scores"
            for c,term1 in enumerate(sorted(index_term.keys()[:-1])):
                for term2 in sorted(index_term.keys()[c:]):
                    # if not bt_weight[term1] == 0.0 or bt_weight[term2] == 0.0:
                    term_sims[term1][term2] += (bt_weight[term1] * bt_weight[term2] * cosim[index_term[term1],index_term[term2]])

    elif args.a == "tags":
        burstscore_terms = defaultdict(list)
        term_freq = {}
        seqstart = j*24
        seqend = seqstart+24
        for i,bt in enumerate(burstyterms):
            print "burstscore",i,"of",len(burstyterms)
            seq = [x for x in term_seqs[bt] if x > 0]
            mean = sum(seq)/len(seq)
            st_dev = gen_functions.return_standard_deviation(seq)
            freq = sum(term_seqs[bt][seqstart:seqend])
            burstscore_terms[bt] = freq-mean-(2*st_dev)
            term_freq[bt] = freq

        burstscore_coocs = defaultdict(lambda : defaultdict(list))
        cooc_freq = defaultdict(lambda : {})
        combis = [comb for comb in combinations(burstyterms, 2)]

                #burstscore_coocs[cooc[0]][cooc[1]] = 0
                #cooc_freq[cooc[0]][cooc[1]] = freq

        #for i,bt in enumerate(sorted(burstyterms)):
        #    for bt2 in sorted(burstyterms)[1:]:
        #        a = burstscore_coocs[bt][bt2]
        #        b1 = burstscore_terms[bt]
        #        b2 = cooc_freq[bt][bt2] / term_freq[bt]
        #        c1 = burstscore_terms[bt2]
        #        c2 = cooc_freq[bt][bt2] / term_freq[bt2]
                #term_sims[bt][bt2] = a + (b1*b2) + (c1*c2)
                #print "a",a,"b1",b1,"b2",b2,"c2",c2,"sim",a+(b1*b2)+(c1*c2)

    #     bursty_cooc_seqs = defaultdict(list)
    #     seqstart = j*24
    #     seqend = seqstart+24
    #     for bt in burstyterms:
    #         bursty_seqs_cooc[bt] = term_seqs[bt][seqstart:seqend]

    #print sims
    outfile = codecs.open(args.o + str(date.month) + "-" + str(date.day) + ".txt","w","utf-8")
    print "printing similarities"
    #print header
    outfile.write(" ".join(burstyterms) + "\n")
    #print vals
    for c,term1 in enumerate(burstyterms[:-1]):
        if c > 0:
            outfile.write(term1 + " " + " ".join([str(term_sims[termpre][term1]) for termpre in burstyterms[:c]]))
        outfile.write(" 1.0 ")
        outfile.write(" ".join([str(term_sims[term1][term2]) for term2 in burstyterms[c+1:]]) + "\n")
    outfile.write(burstyterms[-1] + " " + " ".join([str(term_sims[termpre][burstyterms[-1]]) for termpre in burstyterms[:-1]]) + " 1.0\n")
    outfile.close()
