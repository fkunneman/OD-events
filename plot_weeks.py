import sys
import matplotlib.pyplot as plt
from pylab import *

outplot = sys.argv[1]
xlabel = sys.argv[2]
ylabel = sys.argv[3]
plotfiles = sys.argv[4:]

for pf in plotfiles:
    pf_open = open(pf)
    x = []
    y = []
    for entry in pf_open.readlines():
        # generate coordinates
        tokens = entry.strip().split(" ")
        x.append(int(tokens[0]))
        y.append(float(tokens[1]))
    pf_open.close()
    plt.plot(x,y,linestyle="-",linewidth=3)
# legend = plotfiles[half:]
# plt.legend(legend,loc = "upper right",ncol = 2,bbox_to_anchor=(1.1, 1.2))
plt.ylabel(ylabel)
plt.xlabel(xlabel)
# plt.ylabel("Absolute estimation error (in days)")
# plt.xlabel("Time-to-event in hours")
    #plt.title("\'Micro-f1 score at\' as event time nears")
plt.savefig(outplot)
