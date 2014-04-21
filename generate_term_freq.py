

import sys
import codecs
from collections import defaultdict

outfile = open(sys.arg[1],"w")
infiles = sys.argv[2:]

wordfreq = defaultdict(list)
wordcount = defaultdict(int)

print "counting"
for i,infile in enumerate(infiles):
    print infile
    read = codecs.open(infile,"r","utf-8")
    for line in infile.readlines()[1:]:
        tokens = line.split("\t")
        term = tokens[0]
        wordcount[term] += 1
    read.close()

print "pruning terms"
for term in wordcount.keys():
    if wordcount[term] > 7:
        wordfreq[term] = i * [0]

print "making history"
for i,infile in enumerate(infiles):
    print infile
    read = codecs.open(infile,"r","utf-8")
    for line in infile.readlines()[1:]:
        tokens = line.split("\t")
        term = tokens[0]
        try:
            wordfreq[term][i] = [tokens[1]]
        except:
            continue

for term in wordfreq.keys():
    outfile.write(term + "\t" + "|".join(wordfreq[term]) + "\n")

