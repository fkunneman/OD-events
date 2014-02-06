#! /usr/bin/env python

import sys
import gzip

txt_column = int(sys.argv[1])
tst = gzip.open(sys.argv[2],"wb")
infiles = sys.argv[3:]

cid = 0
l = 9

for f in infiles:
    id_tweets = []
    if f[-2:] == "gz":
        infile = gzip.open(f,"rb")
    else:
        infile = open(f)
    for tweet in infile.readlines():
        zeros = l - len(str(cid))
        tid = zeros * '0' + str(cid)
        tokens = tweet.split(" ")
        meta = tokens[:txt_column]
        txt = [x.decode('utf-8') for x in tokens[txt_column:]]
        id_tweet = "\t".join([zeros] + meta + [" ".join(txt)])
        id_tweets.append(id_tweet)
    infile.close()
    for it in id_tweet:
        tst.write(it)
tst.close()
