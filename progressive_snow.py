
import sys
import os
import re

expdir = sys.argv[1]
trainfile = sys.argv[2]
testfiles = sys.argv[3:]

bs = re.compile(r"p-([\d\.]+)=d-([\d\.]+)=t-([\d\.]+)=c-(\d+)=r-(\d+)=s-([\d\.]+)")
train = trainfile.split("/")[-1]
os.chdir(expdir)
filesdir = "/".join(testfiles.split("/")[:-1]) + "/"
print "filesdir",filesdir
for tf in testfiles:
    test = tf.split("/")[-1]
    num = tf[-1]
    numdir = filesdir + "snow" + num + "/"
    os.mkdir(numdir)
    os.system("cp " + trainfile + " " + expdir)
    os.system("cp " + tf + " " + expdir)
    os.system("paramsearch winnow " + train + " 2")
    paramline = open(train + ".winnow.bestsetting").read()
    params = bs.search(paramline).groups()
    os.system("snow -train -I " + train + " -F test.net -W " + params[0] + "," + params[1] + "," + params[2] + "," + params[3] + ":0-1 -r " + params[4] + " -S " + params[5] + " -c")
    os.system("snow -test -I " + test + " -F test.net -o allactivations > test.out")
    os.system("mv *  " + numdir)
    quit()

