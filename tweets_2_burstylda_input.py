
import sys
from collections import defaultdict
import codecs
import re
import multiprocessing
import lockfile
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

def file_2_usertweets(infiles,q,ch):
    print "Reading in data for",ch
    user_tweets = defaultdict(list)
    for i,infile in enumerate(infiles):
        read = codecs.open(infile,"r","utf-8")
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
        if i in range(5,100,5) or i == len(infiles)-1:
            reserve = []
            for y,user in enumerate(user_tweets.keys()):
                print ch,y
                q.put(user)
                try:
                    userfilename = outdir + re.sub("@","",user) + ".txt"
                    userfile = codecs.open(userfilename,"a","utf-8")
                    lock = lockfile.FileLock(userfilename)
                    lock.acquire()
                    userfile.write("\n".join(user_tweets[user]) + "\n")
                    userfile.close()
                    lock.release()
                except IOError:
                    reserve.append(user)
                # l.acquire()
            x = 0
            while len(reserve) > 0:
                print x,len(reserve)
                try:
                    userfilename = outdir + re.sub("@","",reserve[x]) + ".txt"
                    userfile = codecs.open(userfilename,"a","utf-8")
                    lock = lockfile.FileLock(userfilename)
                    lock.acquire()
                    userfile.write("\n".join(user_tweets[user]) + "\n")
                    userfile.close()
                    lock.release()
                    del(reserve[x])
                except IOError:
                    if x+1 == len(reserve):
                        x = 0
                    else:
                        x += 1
            user_tweets = defaultdict(list)
            # l.release()
        print "done",infile,i,"of",len(infiles),"in",ch

filechunks = gen_functions.make_chunks(infiles)
qu = multiprocessing.Queue()
for j,chunk in enumerate(filechunks):
    p = multiprocessing.Process(target=file_2_usertweets,args=[chunk,qu,j])
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
