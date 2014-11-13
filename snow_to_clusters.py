from __future__ import division
import argparse
import re
from collections import defaultdict
import datetime
import codecs
import multiprocessing
import gen_functions
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
#    print len(tweets)
    cluster_tweets = defaultdict(list)
    for tweet in tweets:
        if tweet.split("\t")[0] == "dutch":
            words = tweet.strip().split("\t")[-1].lower().split(" ")
            swords = set(words)
            for cluster in clusters:
                terms = cluster[1].split(" ")
                #print words,terms,set(words) & set(terms)
                if bool(swords & set(terms)): 
                    cluster_tweets[cluster[0]].append(tweet.strip().split("\t")[-1])                
    queue.put(cluster_tweets)

def rank_tweets(tweets):
#    print tweets
    vectorizer = CountVectorizer(min_df=1)
    X = vectorizer.fit_transform(tweets)
    vectors = X.toarray()
    sumvectors = [0] * len(vectors[0])
    for v in vectors:
        for i,val in enumerate(v):
            sumvectors[i] += val
    centroid = [(x/len(vectors)) for x in sumvectors]
    #calculate cosines
    dists = []
    for i,vector in enumerate(vectors):
        dists.append([i,cosine_similarity(vector,centroid)])
    ranked_tweets = []
    ranked_vectors = []
    dists.sort(key = lambda x : x[1],reverse=True)
    for v in dists:
        vector = vectors[v[0]]
        sim = False
        for v2 in ranked_vectors:
            if cosine_similarity(vector,v2) == 1.0:
                sim = True
        if not sim:
            ranked_tweets.append(tweets[v[0]])
            ranked_vectors.append(vector)
        if len(ranked_tweets) == 10:
            break
    return ranked_tweets

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
    print f
    dates = date.search(f.split("/")[-2]).groups()
    print dates
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
    print (len(clusters)),"clusters in",date,
    for c in clusters:
        c[0] = "0" + str(date.month) + "_" + day + "_" + c[0]
        cluster_data[c[0]].append(c[1]) 
    #collect tweets
    tweets = []
#    print len(tweets)
    try: 
        for f in date_files[date - datetime.timedelta(days=1)]:
            infile = codecs.open(f,"r","utf-8")
            tweets.extend([l.strip() for l in infile.readlines()])
            infile.close()
        for f in date_files[date + datetime.timedelta(days=1)]:
           infile = codecs.open(f,"r","utf-8")
           tweets.extend([l.strip() for l in infile.readlines()])
           infile.close()
    except:
        print "not before or after",date
            
    print len(tweets)
    for f in date_files[date]:
        infile = codecs.open(f,"r","utf-8")
        tweets.extend([l.strip() for l in infile.readlines()])
        infile.close()
    print len(tweets)

    #link clusters to tweets
    print "extracting tweets"    
    q = multiprocessing.Queue()
    tweet_chunks = gen_functions.make_chunks(tweets,dist=True)
    for i in range(len(tweet_chunks)):
        p = multiprocessing.Process(target=extract_tweets,args=[tweet_chunks[i],clusters,q])
        p.start()

    ds = []
    while True:
        l = q.get()
        ds.append(l)
        for clustind in l.keys():
#            print [x[1] for x in clusters if x[0] == clustind]
#            print l[clustind]
            cluster_data[clustind].extend(l[clustind])
        if len(ds) == len(tweet_chunks):
             break

outfile = codecs.open(args.o,"w","utf-8")
for c in classifications:
    if len(cluster_data[c[2]]) > 0:
        print c[2]    
        ranked_tweets = rank_tweets(cluster_data[c[2]][1:])
        outfile.write("\t".join([str(x) for x in c]) + "\t" + cluster_data[c[2]][0] + "\t" + "|".join(ranked_tweets) + "\n")
outfile.close()
