
import sys
import codecs
from collections import defaultdict
import numpy

import annotation_calcs
import gen_functions

sortfile = codecs.open(sys.argv[1],"r","utf-8")
annotationfile = open(sys.argv[2])
outfile = open(sys.argv[3],"w")

cluster_annotations = defaultdict(list)
index_cluster = {}
annotations = []
vals = []

#cluster-annotations
for line in annotationfile.readlines():
    tokens = line.strip().split("\t")
    cluster_annotations[tokens[0]] = [int(x) for x in tokens[1:3]]
annotationfile.close()

#index-cluster
for i,line in enumerate(sortfile.readlines()):
    tokens = line.strip().split("\t")
    index_cluster[i] = tokens[2]
sortfile.close()

#order annotations
for x in sorted(index_cluster):
    cluster = index_cluster[x]
    annotations.append(cluster_annotations[cluster])

#calculate agreement
for i in range(0,1000,125):
    annotationchunk = annotations[i:(i+125)]
    cohens_kappa = annotation_calcs.calculate_cohens_kappa(annotationchunk)
    krippendorff = annotation_calcs.calculate_krippendorffs_alpha(annotationchunk)
    mutual_fscore = annotation_calcs.calculate_mutual_fscore(annotationchunk)
    vals.append([cohens_kappa,krippendorff,mutual_fscore])

#calculate mean
ck = []
ka = []
mf = []
for val in vals:
    outfile.write(" ".join([str(x) for x in val]) + "\n")
    ck.append(val[0])
    ka.append(val[1])
    mf.append(val[2])

for l in [ck,ka,mf]:
#    print l
    mean = numpy.mean(l)
    st_dev = gen_functions.return_standard_deviation(l)
    outfile.write(str(mean) + "(" + str(st_dev) + ") ")

outfile.write("\n")
outfile.write("\n" + str(annotation_calcs.calculate_cohens_kappa(annotations)) + " ")
outfile.write("\n" + str(annotation_calcs.calculate_krippendorffs_alpha(annotations)) + " ")
outfile.write("\n" + str(annotation_calcs.calculate_mutual_fscore(annotationchunk)))
outfile.close()
