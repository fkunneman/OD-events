
import numpy
from scipy.stats import poisson
from operator import itemgetter
import codecs
import sys

seqfile = codecs.open(sys.argv[1],"r","utf-8")

dists = []
kl_table = defaultdict(list)

#make poisson sequence
for line in seqfile.readlines():
    entries = line.strip().split("\t")
    tokens = entries[1].strip("|")
    sequence = [int(x) for x in tokens]
    mean = numpy.mean(sequence)
    po = poisson(mean)
    dists.append([po.pmf(y) for y in sequence])



