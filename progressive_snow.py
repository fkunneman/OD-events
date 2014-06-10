
import sys
import os
import re

expdir = sys.argv[1]
trainfile = sys.argv[2]
testfiles = sys.argv[3:]

bs = re.compile(r"p-([\d\.]+)=d-([\d\.]+)=t-([\d\.]+)=c-(\d+)=r-(\d+)=s-([\d\.]+)")
train = trainfile.split("/")[-1]
print "trainsplit",trainfile.split("/")
os.chdir(expdir)
filesdir = "/".join(trainfile.split("/")[:-1]) + "/"
print "filesdir",filesdir
for tf in testfiles:
    print "testsplit",tf.split("/")
    test = tf.split("/")[-1]
    num = tf[-5]
    numdir = filesdir + "snow" + num
    os.system("mkdir " + numdir)
    print "cp " + trainfile + " ."
    os.system("cp " + trainfile + " .")
    print "ls"
    os.system("ls")
    print "cp " + tf + " ." 
    os.system("cp " + tf + " .")
    print "ls"
    os.system("ls")
    os.system("paramsearch winnow " + train + " 2")
    param = open(train + ".winnow.bestsetting")
    paramline = param.read()
    param.close()
    print param
    params = bs.search(paramline).groups()
    print params
    print "snow -train -I " + train + " -F test.net -W " + params[0] + "," + params[1] + "," + params[2] + "," + params[3] + ":0-1 -r " + params[4] + " -S " + params[5] + " -c"
    os.system("snow -train -I " + train + " -F test.net -W " + params[0] + "," + params[1] + "," + params[2] + "," + params[3] + ":0-1 -r " + params[4] + " -S " + params[5])
    os.system("snow -test -I " + test + " -F test.net -o allactivations > test.out")
    os.system("mv *  " + numdir)

