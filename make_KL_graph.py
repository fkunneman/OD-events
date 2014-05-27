
from scipy.stats import poisson
from operator import itemgetter
import codecs
import sys
import numpy as np
import math
from math import log

seqfile = codecs.open(sys.argv[1],"r","utf-8")

dists = []
kl_table = defaultdict(list)

def kl(p, q):
    p = np.asarray(p, dtype=np.float)
    q = np.asarray(q, dtype=np.float)
    return np.sum(np.where(p != 0,(p-q) * np.log10(p / q), 0))

#make poisson sequences
for line in seqfile.readlines():
    entries = line.strip().split("\t")
    tokens = entries[1].strip("|")
    sequence = [int(x) for x in tokens]
    mean = np.mean(sequence)
    po = poisson(mean)
    dists.append([po.pmf(y) for y in sequence])

#calculate KL

for dist in dists:


