
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

def file_2_usertweets(infiles,q,ch):
    print "Reading in data for",ch
    for i,infile in enumerate(infiles):
        read = codecs.open(infile,"r","utf-8")
        for line in read.readlines():
            tokens = line.strip().split("\t")
            try:
                text = tokens[textcol].split(" ")
                if len(text) >= 3:
                    filtered = " ".join([x for x in text if x not in sw])
                    user = tokens[usercol]
                    date = tokens[datecol]
                    time = tokens[timecol]
                    queue.put([user,date + " " + time + ":" + filtered] + "\n")
            except IndexError:
                continue
        read.close()
        print "done",infile,i,"of",len(infiles),"in",ch

filechunks = gen_functions.make_chunks(infiles)
qu = multiprocessing.Queue()
for j,chunk in enumerate(filechunks):
    p = multiprocessing.Process(target=file_2_usertweets,args=[chunk,qu,j])
    p.start()

while True:
    user_tweet = qu.get()
    users = list(set(users.append(user_tweet[0])))
    userfile = codecs.open(outdir + re.sub("@","",user_tweet[0]) + ".txt","a","utf-8")
    userfile.write(user_tweet[1])
    userfile.close()

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
