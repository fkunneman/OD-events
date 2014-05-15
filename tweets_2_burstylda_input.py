
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
langcol = int(sys.argv[4])
textcol = int(sys.argv[5])
outdir = sys.argv[6]
stopwords = codecs.open(sys.argv[7],"r","utf-8")
infiles = sys.argv[8:]

sw = [li.replace('.','\.') for li in stopwords.read().split("\n")] # not to match anything with . (dot)

def count_authortweets(infls,q,ch):
    print "Reading in data for",ch
    user_tweets = defaultdict(int)
    for i,infile in enumerate(infls):
        read = codecs.open(infile,"r","utf-8")
        for line in read.readlines():
            tokens = line.strip().split("\t")
            try:
                if tokens[langcol] == "dutch" and len(tokens[textcol].split(" ")) >= 3:
                    user = tokens[usercol]
                    user_tweets[user] += 1
            except IndexError:
                print "INDEXERROR!",infile,i,ch
                continue
        read.close()
    q.put(user_tweets)

def write_usertweets(inf,um,userl,ch):
    print "Reading in data for",ch,"num_users:",len(userl)
    # open userfiles
    for u in userl:
        um[u] = True
    user_tweets = defaultdict(list)
    for i,infile in enumerate(inf):
        read = codecs.open(infile,"r","utf-8")
        for line in read.readlines():
            tokens = line.strip().split("\t")
            try:
                if um[tokens[usercol]]:
                    text = tokens[textcol].lower().split(" ")
                    if tokens[langcol] == "dutch" and len(text) >= 3:
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
fivehundred = True
twohundred = True
hundred = True
#fifty = True
#twenty = True

filelist500 = codecs.open(outdir + "filelist500.txt","w","utf-8")
filelist200 = codecs.open(outdir + "filelist200.txt","w","utf-8")
filelist100 = codecs.open(outdir + "filelist100.txt","w","utf-8")
user_match = {}
for i,user_c in enumerate(usertweets_sorted):
    if user_c[1] < 100:
        userindex = i
        print user_c[1],"<100"
        break
    elif user_c[1] < 200 
        filelist100.write(re.sub("@","",user_c[0]) + "\n")
        print user_c[1],"<200"
    elif user_c[1] < 500:
        filelist200.write(re.sub("@","",user_c[0]) + "\n")
        filelist100.write(re.sub("@","",user_c[0]) + "\n")
        print user_c[1],"<500"
    else:
        filelist500.write(re.sub("@","",user_c[0]) + "\n")
        filelist200.write(re.sub("@","",user_c[0]) + "\n")
        filelist100.write(re.sub("@","",user_c[0]) + "\n")
        print user_c[1],">500"
filelist500.close()
filelist200.close()
filelist100.close()

print "num_authors:",userindex
filtered_users = [x[0] for x in usertweets_sorted[:userindex]]
del usertweets_sorted[0:len(usertweets_sorted)]

print "Writing clusters to files"
userchunks = gen_functions.make_chunks(filtered_users)
for j,chunk in enumerate(userchunks):
    print chunk
    p = multiprocessing.Process(target=write_usertweets,args=[infiles,user_match.copy(),chunk,j])
    p.start()
