import sys
import matplotlib.pyplot as plt
import codecs
import datetime

termfile = codecs.open(sys.argv[1],"r","utf-8")
time_begin = int(sys.argv[2])
time_end = int(sys.argv[3])
outplot = sys.argv[4]
terms = sys.argv[5:]

termseqs = []
legend = []

#extract term seqs
termseqs = [x for x in termfile.readlines() if x.split("\t")[0] in terms]

#plot term seqs
time_start = datetime.datetime(2013,6,22,0,0,0)
for ts in termseqs:
    tokens = ts.strip().split("\t")
    legend.append(tokens[0])
    seq = tokens[1].split("|")
    i = time_begin
    x = []
    y = []
    while i <= time_end:
        x.append(time_start + datetime.timedelta(hours=i))
        y.append(seq[i])
        plt.plot(x,y,linestyle="-",linewidth=3)
        i+=1

plt.legend(legend,loc = "upper right",ncol = 1,bbox_to_anchor=(1.1, 1.2))
plt.ylabel("Unigram frequency")
plt.xlabel("date and time")
plt.savefig(outplot)
