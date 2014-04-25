
import sys
from collections import defaultdict
import codecs

#author-tweets dict
usercol = int(sys.argv[1])
datecol = int(sys.argv[2])
timecol = int(sys.argv[3])
textcol = int(sys.argv[4])
outdir = sys.argv[5]
infiles = sys.argv[6:]

user_tweets = defaultdict(list)

print "Reading in data"
for i,infile in enumerate(infiles):
    print infile
    read = codecs.open(infile,"r","utf-8")
    for line in read.readlines()[1:]:
        tokens = line.strip().split("\t")
        text = tokens[textcol]
        if len(text.split(" ")) >= 3 and tokens[0] == "dutch":
            user = tokens[usercol]
            date = tokens[datecol]
            time = tokens[timecol]
            user_tweets[user].append(date + " " + time + ":" + text) 
    read.close()

for user in user_tweets.keys():
    outfile = codecs.open(outdir + re.sub("@","",user) + ".txt","w","utf-8")
    outfile.write("\n".join(user_tweets[user]))
    outfile.close()
