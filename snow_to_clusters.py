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
        words = list(set(tweet.split("\t")[-1].split(" ")))
        for cluster in clusters:
            terms = [x[0] for x in cluster[2]]
            if len(set(words) & set(terms)) >= 1:
                tokens = tweet.split("\t")
                if tokens[0] == "dutch":
                    words = tokens[-1].split(" ")
                    hashtags = len([x for x in words if re.search("^#",x)])
                    urls = len([x for x in words if re.search("^http://",x)])
                    if re.search("^@",words[0]):
                        reply = 1
                    else:
                        reply = 0
                    mentions = len([x for x in words[1:] if re.search("^@",x)])
                    cluster_tweets[cluster[0]].append([len(set(words) & set(terms)),hashtags,urls,reply,mentions,tokens[2],tokens[-1]])                
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
    index_cluster[tokens[0]] = tokens[1]
ic.close()    

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
    clusters = [x.strip().split("\t")[1] for x in infile.readlines()]
    infile.close()
    date_clusters[datetime.date(int(dates[0]),int(dates[1]),int(dates[2]))] = clusters

print date_clusters

# for date in 
# for c in classifications[:1000]:

    






# print "making bursty term graph"
# #make date-burstyterm-graph
# burstyfile = codecs.open(args.b,"r","utf-8")
# bursties = {}
# for line in burstyfile.readlines():
#     tokens = line.strip().split("\t")
#     bursties[tokens[0]] = float(tokens[1])
# burstyfile.close()

# #for each date
# for j,date in enumerate(sorted(date_files.keys())):
#     print date
#     #collect tweets
#     tweets = []
#     for f in date_files[date]:
#         infile = codecs.open(f,"r","utf-8")
#         tweets.extend([l.strip() for l in infile.readlines()])
#         infile.close()
#     #extract clusters
#     clusters = []
#     for i,line in enumerate(date_clusters[date]):
#         units = line.split("\t")
#         mean_sim = units[0]
#         terms = [x.split(" ") for x in units[1:]]
#         clusters.append([i,mean_sim,terms])
#     #link clusters to tweets
#     print "extracting tweets"    
#     q = multiprocessing.Queue()
#     cluster_chunks = gen_functions.make_chunks(clusters,dist=True)
#     for i in range(len(cluster_chunks)):
#         p = multiprocessing.Process(target=extract_tweets,args=[tweets,cluster_chunks[i],q])
#         p.start()

#     ds = []
#     while True:
#         l = q.get()
#         ds.append(l)
#         for clustind in l.keys():
#             l[clustind].sort(key=lambda x : x[0],reverse=True)
#             #print l[clustind]
#             clusters[clustind].append(l[clustind])
#         if len(ds) == len(cluster_chunks):
#             break
