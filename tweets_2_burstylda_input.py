
import sys
from collections import defaultdict
import codecs
import re
import multiprocessing
import gen_functions

#author-tweets dict
usercol = int(sys.argv[1])
datecol = int(sys.argv[2])
timecol = int(sys.argv[3])
textcol = int(sys.argv[4])
outdir = sys.argv[5]
stopwords = codecs.open(sys.argv[6],"r","utf-8")
infiles = sys.argv[7:]

sw = [li.replace('.','\.') for li in stopwords.read().split("\n")] # not to match anything with . (dot)

def count_authortweets(infiles,q,ch):
    print "Reading in data for",ch
    user_tweets = defaultdict(int)
    for i,infile in enumerate(infiles):
        read = codecs.open(infile,"r","utf-8")
        for line in read.readlines():
            tokens = line.strip().split("\t")
            try:
                user = tokens[usercol]
                user_tweets[user] += 1
            except IndexError:
                print "INDEXERROR!",infile,i,ch
                continue
        read.close()
    q.put(user_tweets)

def write_usertweets(userl,ch):
    print "Reading in data for",ch,"num_users:",len(userl)
    # open userfiles
    user_tweets = defaultdict(list)
    for i,infile in enumerate(infiles):
        read = codecs.open(infile,"r","utf-8")
        for line in read.readlines():
            tokens = line.strip().split("\t")
            try:
                if tokens[usercol] in userl:
                    text = tokens[textcol].lower().split(" ")
                    if len(text) >= 3:
                        filtered = " ".join([x for x in text if x not in sw])
                        user = tokens[usercol]
                        date = tokens[datecol]
                        time = tokens[timecol]
                        user_tweets[user].append(date + " " + time + ":" + filtered)
            except IndexError:
                print "INDEXERROR!",infile,i,ch
                continue
        read.close()
        if i in range(5,2500,5) or i == len(infiles)-1:
            for y,user in enumerate(user_tweets.keys()):
                userfilename = outdir + re.sub("@","",user) + ".txt"
                userfile = codecs.open(userfilename,"a","utf-8")
                userfile.write("\n".join(user_tweets[user]) + "\n")
                userfile.close()
            user_tweets = defaultdict(list)
        print "done",infile,i,"of",len(infiles),"in",ch

print "Generating author-tweetcount dict"
filechunks = gen_functions.make_chunks(infiles)
qu = multiprocessing.Queue()
for j,chunk in enumerate(filechunks):
    p = multiprocessing.Process(target=count_authortweets,args=[chunk,qu,j])
    p.start()

ds = []
while True:
    l = qu.get()
    ds.append(l)
    if len(ds) == len(filechunks):
        break

usertweets_total = defaultdict(int)
for d in ds:
    for k in d:
        usertweets_total[k] += d[k]
    d.clear()
usertweets_sorted = sorted(usertweets_total.items(), key=lambda x: x[1],reverse=True)
usertweets_total.clear()

print "selecting authors"
for i,user_c in enumerate(usertweets_sorted):
    if user_c[1] < 10:
        userindex = i
print "num_authors:",userindex
filtered_users = [x[0] for x in usertweets_sorted[:userindex]]
del usertweets_sorted[0:len(usertweets_sorted)]

print "Writing clusters to files"
userchunks = gen_functions.make_chunks(filtered_users)
for j,chunk in enumerate(userchunks):
    p = multiprocessing.Process(target=write_usertweets,args=[chunk,j])
    p.start()
