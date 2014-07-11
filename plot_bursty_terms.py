import sys
import matplotlib.pyplot as plt
from numpy import arange
import codecs
import datetime
from collections import defaultdict
import matplotlib.ticker as ticker
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange

termfile = codecs.open(sys.argv[1],"r","utf-8")
time_begin = int(sys.argv[2])
time_end = int(sys.argv[3])
outplot = sys.argv[4]
terms = sys.argv[5:]

termseqs_order = defaultdict(list)

#extract term seqs
termseqs = [x for x in termfile.readlines() if x.split("\t")[0] in terms]

#plot term seqs
time_start = datetime.datetime(2013,6,22,0,0,0)
linestyles = ["-","-","--","|"]
for ts in termseqs:
    tokens = ts.strip().split("\t")
    l = tokens[0]
    seq = tokens[1].split("|")
    termseqs_order[l] = seq

fig, ax = plt.subplots()
for j,term in enumerate(terms):
    seq = termseqs_order[term]
    i = time_begin
    x = []
    y = []
    while i <= time_end:
        x.append((time_start + datetime.timedelta(hours=i)))
        y.append(seq[i])
        i+=1
    ax.plot(x,y,linestyle=linestyles[j],linewidth=2)

#numpy.array([base + datetime.timedelta(hours=i) for i in xrange(24)])

#ax.xticks(np.array([min(x) + datetime.timedelta(hours=i) for i in range(0,time_end - time_begin,6)]))
#plt.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
#ax.xaxis.set_major_locator( DayLocator() )
ax.xaxis.set_major_locator( HourLocator(arange(0,time_end-time_begin,6)) )
ax.xaxis.set_major_formatter( DateFormatter('13/%m/%d %H:00') )
ax.fmt_xdata = DateFormatter('%Y-%m-%d %H:%M:%S')
fig.autofmt_xdate()
ax.xaxis_date()
#fig.autofmt_xdate()
plt.legend(terms,loc = "upper right",ncol = 1)
plt.ylabel("Unigram frequency")
plt.xlabel("date and time")
plt.savefig(outplot)
