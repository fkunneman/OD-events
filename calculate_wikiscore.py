#!/usr/bin/env python

from __future__ import division
import argparse
import codecs
from collections import defaultdict
import xml.etree.ElementTree as etree


"""
Script to calculate the relative wikipedia anchors for a given list of words.
"""
parser = argparse.ArgumentParser(description = "Script to calculate the relative wikipedia anchors for a given list of words.")
parser.add_argument('-w', action = 'store', required = True, help = "The file with the Wikipedia dump")  
parser.add_argument('-b', action = 'store', required = True, help = "the file with bursty terms")
parser.add_argument('-o', action = 'store', required = True, help = "the output files for anchor scores per term")

args = parser.parse_args()

outfile = codecs.open(args.o,"w","utf-8")
bursty_matches = defaultdict(lambda : defaultdict(int))

#load in bursty terms 
print "loading in bursty terms"
burstyfile = codecs.open(args.b,"r","utf-8")
bursties = []
for line in burstyfile.readlines():
    tokens = line.strip().split("\t")
    bursties.append(tokens[0])
burstyfile.close()
bursties_set = set(bursties)
bursties_anchor = ["[[" + x + "]]" for x in bursties]
bursties_anchor.extend(["[[" + x for x in bursties])
bursties_anchor.extend([x + "]]" for x in bursties])
bursties_anchor_set = set(bursties_anchor)

# print "loading in wikipedia dump"
# #load in Wikipedia dump
# xmldoc = minidom.parse(args.w)
# pages = xmldoc.getElementsByTagName('page')

#for each page
print "matching terms to pages"
for event, elem in etree.iterparse(args.w, events=('start', 'end', 'start-ns', 'end-ns')):
    if event == 'end':
        if elem.tag == '{http://www.mediawiki.org/xml/export-0.8/}text':
            words = elem.text.split(" ")

# for i,page in enumerate(pages):
#     print i,"of",len(pages),"pages"
#     text = page.getElementsByTagName('text')[0]
    
    #check if one of the bursty terms is present
            if bool(bursties_set & set(words)):
                matches = list(bursties_set & set(words))
                for match in matches:
                    bursty_matches[match]["word"] += 1
            if bool(bursties_anchor_set & set(words)):
                matches = list(bursties_anchor_set & set(words))
                for match in matches:
                    stripped_match = re.sub("[\[\]]","",match)
                    bursty_matches[stripped_match]["anchor"] += 1

#calculate newsworthiness
print "writing newsworthiness to file"
for b in bursty_matches.keys():
    newsworthiness = bursty_matches[b]["anchor"] / bursty_matches[b]["word"]
    outfile.write(b + "\t" + str(newsworthiness) + "\n")
