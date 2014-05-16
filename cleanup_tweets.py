
import sys
from collections import defaultdict
import codecs
import re
import multiprocessing
import gen_functions

#author-tweets dict
langcol = int(sys.argv[1])
textcol = int(sys.argv[2])
outdir = sys.argv[3]
stopwords = codecs.open(sys.argv[4],"r","utf-8")
infiles = sys.argv[5:]

sw = [li.replace('.','\.') for li in stopwords.read().split("\n")] # not to match anything with . (dot)

def cleanup_tweets(infls,ch):
    print "Reading in data for",ch
    for i,infile in enumerate(infls):
        print "done",i,"of",len(infls),"in",ch
        read = codecs.open(infile,"r","utf-8")
        wr = codecs.open(outdir + "/".join(infile.split("/")[-1:]),"w","utf-8")
        for line in read.readlines():
            tokens = line.strip().split("\t")
            try:
#            print tokens, langcol, textcol
                if tokens[langcol] == "dutch" and not re.search(r"^rt",tokens[textcol]):
                    text = tokens[textcol].lower().split(" ")
                    filtered = " ".join([x for x in text if x not in sw and not re.search(r"^@",x)])
                    tokens[textcol] = filtered
                    wr.write("\t".join(tokens) + "\n")
            except IndexError:
                print "INDEXERROR!",infile,i,ch
                continue
        read.close()
        wr.close()
    
filechunks = gen_functions.make_chunks(infiles)
for j,chunk in enumerate(filechunks):
    p = multiprocessing.Process(target=cleanup_tweets,args=[chunk,j])
    p.start()
