
import sys
from collections import defaultdict

labelfile = open(sys.argv[1],"w")
annotationfiles = sys.argv[2:]

cluster_annotations = defaultdict(list)

for af in annotationfiles:
    print af
    r = open(af)
    for l in r.readlines()[2:]:
#        print l
        tokens = l.strip().split("\t")
#        print tokens
#        print tokens
        try:
            cid = tokens[1]
        except:
            continue
        eventlabel = tokens[2][0]
        sociallabelstring = tokens[3]
        if len(sociallabelstring) > 0:
            sociallabel = '1'
        else:
            sociallabel = '0'

        if cluster_annotations.has_key(cid):
            cluster_annotations[cid].append(sociallabel)
            cluster_annotations[1] = eventlabel
        else:
            cluster_annotations[cid] = [eventlabel,sociallabel]
    r.close()

for cid in cluster_annotations.keys():
    labelfile.write(cid + "\t" + "\t".join(cluster_annotations[cid]) + "\n")
labelfile.close()
