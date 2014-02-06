#! /usr/bin/env python

import sys
import gzip

txt_column = int(sys.argv[1])
infiles = sys.argv[2:]

cid = 0
l = 9

for f in infiles:
    print f
    id_tweets = []
    if f[-2:] == "gz":
        infile = gzip.open(f,"rb")
    else:
        infile = open(f)
    for tweet in infile.readlines():
        zeros = l - len(str(cid))
        tid = zeros * '0' + str(cid)
        tokens = tweet.decode('utf-8').split(" ")
        meta = tokens[:txt_column]
        txt = tokens[txt_column:]
        id_tweet = "\t".join([tid] + meta + [" ".join(txt)])
        id_tweets.append(id_tweet)
        cid += 1
    infile.close()
    outfile = gzip.open(f,"wb")
    for it in id_tweets:
        outfile.write(it.encode('utf-8'))
    outfile.close()
