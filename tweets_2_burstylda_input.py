
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

user_tweets = defaultdict(list)

sw = [li.replace('.','\.') for li in stopwords.read().split("\n")] # not to match anything with . (dot)
num_tweets = 0
users = []

def file_2_usertweets(infiles,l,q,ch):
    print "Reading in data for",ch
    for i,infile in enumerate(infiles):
        read = codecs.open(infile,"r","utf-8")
        user_tweets = defaultdict(list)
        for line in read.readlines():
            tokens = line.strip().split("\t")
            try:
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
        for user in user_tweets.keys():
            q.put(user)
            l.acquire()
            userfile = codecs.open(outdir + re.sub("@","",user) + ".txt","a","utf-8")
            userfile.write("\n".join(user_tweets[user]) + "\n")
            userfile.close()
            l.release()
        print "done",infile,i,"of",len(infiles),"in",ch

filechunks = gen_functions.make_chunks(infiles)
qu = multiprocessing.Queue()
lock = multiprocessing.Lock()
for j,chunk in enumerate(filechunks):
    p = multiprocessing.Process(target=file_2_usertweets,args=[chunk,lock,qu,j])
    p.start()

while True:
    users.append(qu.get())

users = list(set(users))
usersfile = codecs.open("userlist.txt","utf-8","w")
for user in users:
    usersfile.write(user + "\n")
usersfile.close()   




 


# print "Writing user files"
# users = codecs.open(outdir + "all_users.txt","w","utf-8")
# for user in user_tweets.keys():
#     userfile = re.sub("@","",user) + ".txt"
#     users.write(userfile + "\n")
#     outfile = codecs.open(outdir + userfile,"w","utf-8")
#     outfile.write("\n".join(user_tweets[user]))
#     outfile.close()
# users.close()
