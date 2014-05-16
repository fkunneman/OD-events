
import sys
import codecs
import re

rankfile = codecs.open(sys.argv[1],"r","utf-8")
new_file = codecs.open(sys.argv[2],"w","utf-8")

aj = re.compile(r"ajax",re.IGNORECASE)
fey = re.compile(r"feyenoord",re.IGNORECASE)
ns = re.compile(r"ns")
user = re.compile(r"USER")

for line in rankfile.readlines():
    tokens = line.strip.split("\t")
    text = tokens[-1]
    if not aj.search(text) and not fey.search(text) and not ns.search(text) and not user.match(text):
        new_file.write(line)
rankfile.close()
new_file.close()
