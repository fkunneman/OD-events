
import sys
import codecs
from collections import defaultdict

outfile = codecs.open(sys.argv[1],"w","utf-8")
termtype = sys.argv[2] #either 'uni' or 'cooc'
infiles = sys.argv[3:]

wordfreq = defaultdict(list)
wordcount = defaultdict(int)
include = {}

cooc = False
if termtype == "cooc":
    cooc = True

print "counting"
if cooc:
    print "cooc counting"
    for i,infile in enumerate(infiles):
        print infile
        idict = defaultdict(int)
        read = codecs.open(infile,"r","utf-8")
        for line in read.readlines()[1:]:
            tokens = line.split("\t")
            if not tokens[0] == tokens[1]:
                term = min(tokens[0],tokens[1]) + " " + max(tokens[0],tokens[1])
                idict[term] = int(tokens[2])
        read.close()
        for k in idict:
            wordcount[k] += idict[k]
        idict.clear()
else:
    for i,infile in enumerate(infiles):
        print infile
        read = codecs.open(infile,"r","utf-8")
        for line in read.readlines()[1:]:
            tokens = line.split("\t")
            term = tokens[0]
            wordcount[term] += int(tokens[1])
        read.close()

print "pruning terms"
for term in wordcount.keys():
    if wordcount[term] >= 10:
        wordfreq[term] = (i+1) * ['0']
        include[term] = True
    else:
        include[term] = False

print "making history"
for i,infile in enumerate(infiles):
    print infile
    read = codecs.open(infile,"r","utf-8")
    for line in read.readlines()[1:]:
        tokens = line.split("\t")
        if cooc:
            if not tokens[0] == tokens[1]:
                term = min(tokens[0],tokens[1]) + " " + max(tokens[0],tokens[1])
                if include[term]:
                    wordfreq[term][i] = tokens[2]
        else:
            term = tokens[0]
            if include[term]:
                wordfreq[term][i] = tokens[1]

for term in wordfreq.keys():
    if max([int(x) for x in wordfreq[term]]) >= 10:
        outfile.write(term + "\t" + "|".join(wordfreq[term]) + "\n")
