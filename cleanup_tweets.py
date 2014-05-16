
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
#            print tokens
            try:
#            print tokens, langcol, textcol
                #print tokens[textcol]
                if tokens[langcol] == "dutch":
                    #print "ja"
                    text = tokens[textcol].lower().split(" ")
                    if not re.search("rt",text[0]):
                        filtered = " ".join([x for x in text if x not in sw and not re.search(r"^@",x)])
                        if len(filtered.split(" ")) >= 3:
                            tokens[textcol] = filtered
#                    print "write","\t".join(tokens + "\n")
                            wr.write("\t".join(tokens) + "\n")
            except IndexError:
                print "INDEXERROR!",tokens,infile,i,ch
                continue
        read.close()
        wr.close()
    
filechunks = gen_functions.make_chunks(infiles)
for j,chunk in enumerate(filechunks):
    p = multiprocessing.Process(target=cleanup_tweets,args=[chunk,j])
    p.start()
