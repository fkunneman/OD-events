import sys
import codecs
from collections import defaultdict

sorted = open(sys.argv[1],"r")
text = codecs.open(sys.argv[2],"r","utf-8")
outfile = codecs.open(sys.argv[3],"w","utf-8")

clusts = [int(x.split("\t")[0]) for x in sorted.readlines()[:250]]

clust_tweets = defaultdict(list)

for line in text.readlines():
    c = int(line.split("\t")[0])
    clust_tweets[c].append(line.strip())         

for c in clusts:
    outfile.write("\n".join(clust_tweets[c]) + "\n")


