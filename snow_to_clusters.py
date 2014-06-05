import argparse
import re
from collections import defaultdict
import datetime
import codecs

parser = argparse.ArgumentParser(description = "Script to rank and summarize the extracted events on a day")
parser.add_argument('-i', action = 'store', nargs='+',required = True, help = "The files with tweets per hour")  
parser.add_argument('-f', action = 'store', nargs='+',required = True, help = "the file with event clusters")
parser.add_argument('-s', action = 'store', required = True, help = "the classifier output")
parser.add_argument('--ic', action = 'store', required = True, help = "the index-clusterfile")
parser.add_argument('-o', action = 'store', required = True, help = "the file to write output to")

args = parser.parse_args()
classificationfile = open(args.s)
ic = open(args.ic)

def extract_tweets(tweets,clusters,queue):
    cluster_tweets = defaultdict(list)
    for tweet in tweets:
        words = list(set(tweet.strip().split("\t")[-1].split(" ")))
        for cluster in clusters:
            terms = cluster[1].split(" ")
            if len(set(words) & set(terms)) == len(terms): 
                cluster_tweets[cluster[0]].append(tweet.strip().split("\t")[-1])                
    queue.put(cluster_tweets)

classifications = []
conf = re.compile(r"(0\.\d+)")
i = 0
for line in classificationfile:
    #tokens = line.strip().split(r"\s+")
    #print tokens
    if re.search(r"^1:",line):
#        print line,conf.search(line)
        c = conf.search(line).groups()[0]
        classifications.append([i,float(c)])
        i += 1
classificationfile.close()

classifications.sort(key = lambda x : x[1],reverse=True)

index_cluster = {}
for i in ic.readlines():
    tokens = i.strip().split(" ")
    index_cluster[int(tokens[0])] = tokens[1]
ic.close()    

cluster_rank = {}
clusters_ranked = []
for c in classifications[:1000]:
    c.append(index_cluster[c[0]])
    cluster_rank[index_cluster[c[0]]] = c[0]
    clusters_ranked.append(index_cluster[c[0]])

#cluster files by date
date_files = defaultdict(list)
date = re.compile(r"(\d{4})(\d{2})(\d{2})-")
for f in args.i:
    dates = date.search(f).groups()
    date_files[datetime.date(int(dates[0]),int(dates[1]),int(dates[2]))].append(f)

#make date-cluster dict
date_clusters = defaultdict(list)
date = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
for f in args.f:
    dates = date.search(f.split("/")[-2]).groups()
    infile = codecs.open(f,"r","utf-8")
    clusters = [x.strip().split("\t")[:2] for x in infile.readlines()]
    infile.close()
    date_clusters[datetime.date(int(dates[0]),int(dates[1]),int(dates[2]))] = clusters

cluster_data = defaultdict(list)
for date in date_clusters.keys():
    print "month",date.month,"day",date.day,"cluster",date_clusters[date][0][0]
    if len(str(date.day)) == 2:
        day = str(date.day)
    else:
        day = "0" + str(date.day)    
    shab = "0" + str(date.month) + "_" + day + "_"
    clusters = [x for x in date_clusters[date] if shab + x[0] in clusters_ranked]
    print (len(clusters)),"clusters in",date, clusters
    quit()
    for c in clusters:
        cluster_data[c[0]].append(c[1]) 
    #collect tweets
    tweets = []
    for f in date_files[date]:
        infile = codecs.open(f,"r","utf-8")
        tweets.extend([l.strip() for l in infile.readlines()])
        infile.close()
    #link clusters to tweets
    print "extracting tweets"    
    q = multiprocessing.Queue()
    tweet_chunks = gen_functions.make_chunks(tweets,dist=True)
    for i in range(len(tweet_chunks)):
        p = multiprocessing.Process(target=extract_tweets,args=[tweetchunks[i],clusters,q])
        p.start()

        ds = []
        while True:
            l = q.get()
            ds.append(l)
            for clustind in l.keys():
                #print l[clustind]
                cluster_data[clustind].append(l[clustind])
            if len(ds) == len(cluster_chunks):
                break

outfile = codecs.open(args.o,"w","utf-8")
for c in classifications:
    outfile.write("\t".join(c) + "\t" + cluster_data[c[2]][0] + "\t" + "|".join(cluster_data[c[2]][1:]) + "\n")
outfile.close()
