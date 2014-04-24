
import sys
import codecs
from collections import defaultdict

outfile = codecs.open(sys.argv[1],"w","utf-8")
infiles = sys.argv[2:]

wordfreq = defaultdict(list)
wordcount = defaultdict(int)
include = {}

print "counting"
for i,infile in enumerate(infiles):
    print infile
    read = codecs.open(infile,"r","utf-8")
    for line in read.readlines()[1:]:
        tokens = line.split("\t")
        term = tokens[0]
        wordcount[term] += 1
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
        term = tokens[0]
        wordfreq[term][i] = tokens[1]

for term in wordfreq.keys():
    if max(wordfreq[term]) >= 10:
        outfile.write(term + "\t" + "|".join(wordfreq[term]) + "\n")
