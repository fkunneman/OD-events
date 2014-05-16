
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
# langcol = int(sys.argv[4])
textcol = int(sys.argv[4])
outdir = sys.argv[5]
# stopwords = codecs.open(sys.argv[7],"r","utf-8")
infiles = sys.argv[6:]

# sw = [li.replace('.','\.') for li in stopwords.read().split("\n")] # not to match anything with . (dot)

def count_authortweets(infls,q,ch):
    print "Reading in data for",ch
    user_tweets = defaultdict(int)
    for i,infile in enumerate(infls):
        read = codecs.open(infile,"r","utf-8")
        for line in read.readlines():
            tokens = line.strip().split("\t")
            # try:
#            print tokens, langcol, textcol
            # if tokens[langcol] == "dutch" and len(tokens[textcol].split(" ")) >= 3 and not re.search(r"^rt",tokens[textcol]):
            user_tweets[tokens[usercol]] += 1
            # else:
            #     user_tweets[user] = user_tweets[user]
            # except IndexError:
            #     print "INDEXERROR!",infile,i,ch
            #     continue
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
#            print tokens,usercol,tokens[usercol]
            # try:
            if um[tokens[usercol]]:
                # text = tokens[textcol].lower().split(" ")
                text = tokens[textcol]
                # if tokens[langcol] == "dutch" and len(text) >= 3 and not re.search(r"^rt",tokens[textcol]):
                #     filtered = " ".join([x for x in text if x not in sw and not re.search(r"^@",x)])
                #     if len(filtered) >= 3:
                user = tokens[usercol]
                date = tokens[datecol]
                time = tokens[timecol]
                userfilename = outdir + "input/" + re.sub("@","",user) + ".txt"
                userfile = codecs.open(userfilename,"a","utf-8")
                userfile.write(date + " " + time + ":" + text + "\n")
                # userfile.write("\n".join(user_tweets[user]) + "\n")
                userfile.close()
                # user_tweets[user].append(date + " " + time + ":" + filtered)
            # except IndexError:
            #     print "INDEXERROR!",infile,i,ch
            #     continue
            # except KeyError:
            #     print "KEYERROR!",infile,i,ch
        read.close()
        # if i in range(5,2500,5) or i == len(infiles)-1:
        #     for y,user in enumerate(user_tweets.keys()):
        #         userfilename = outdir + "input/" + re.sub("@","",user) + ".txt"
        #         userfile = codecs.open(userfilename,"a","utf-8")
        #         userfile.write("\n".join(user_tweets[user]) + "\n")
        #         userfile.close()
        #     user_tweets = defaultdict(list)
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
#fivehundred = True
#twohundred = True
fifty = True
#fifty = True
#twenty = True

fl500 = []
fl200 = []
fl100 = []
fl50 = []
user_match = {}
for i,user_c in enumerate(usertweets_sorted):
    user_match[user_c[0]] = False
    if user_c[1] < 50 and fifty:
        userindex=1
        fifty = False
    if user_c[1] < 100 and hundred:
        fl50.append(re.sub("@","",user_c[0]))
#        print user_c[1],"<100"
    elif user_c[1] < 200: 
        fl100.append(re.sub("@","",user_c[0]))
        fl50.append(re.sub("@","",user_c[0]))
#        print user_c[1],"<200"
    elif user_c[1] < 500:
        fl200.append(re.sub("@","",user_c[0]))
        fl100.append(re.sub("@","",user_c[0]))
        fl50.append(re.sub("@","",user_c[0]))
#        print user_c[1],"<500"
    else:
        fl500.append(re.sub("@","",user_c[0]))
        fl200.append(re.sub("@","",user_c[0]))
        fl100.append(re.sub("@","",user_c[0]))
        fl50.append(re.sub("@","",user_c[0]))
#        print user_c[1],">500"
    # user_match

filelist500 = codecs.open(outdir + "filelist500.txt","w","utf-8")
filelist200 = codecs.open(outdir + "filelist200.txt","w","utf-8")
filelist100 = codecs.open(outdir + "filelist100.txt","w","utf-8")
filelist50 = codecs.open(outdir + "filelist50.txt","w","utf-8")
filelist500.write("\n".join(fl500))
filelist200.write("\n".join(fl200))
filelist100.write("\n".join(fl100))
filelist50.write("\n".join(fl50))
filelist500.close()
filelist200.close()
filelist100.close()
filelist50.close()

#print user_match

print "num_authors:",userindex
filtered_users = [x[0] for x in usertweets_sorted[:userindex]]
#del usertweets_sorted[0:len(usertweets_sorted)]

print "Writing clusters to files"
userchunks = gen_functions.make_chunks(filtered_users,dist=True)
for j,chunk in enumerate(userchunks):
#    print chunk
    p = multiprocessing.Process(target=write_usertweets,args=[infiles,user_match.copy(),chunk,j])
    p.start()
