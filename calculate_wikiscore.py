#!/usr/bin/env python

import argparse
import codecs
from collections import defaultdict
from xml.dom import minidom


"""
Script to calculate the relative wikipedia anchors for a given list of words.
"""
parser = argparse.ArgumentParser(description = "Script to calculate the relative wikipedia anchors for a given list of words.")
parser.add_argument('-w', action = 'store', required = True, help = "The file with the Wikipedia dump")  
parser.add_argument('-b', action = 'store', required = True, help = "the file with bursty terms")
parser.add_argument('-o', action = 'store', required = True, help = "the output files for anchor scores per term")

args = parser.parse_args()

bursty_matches = defaultdict(lambda : defaultdict(int))

#load in bursty terms 
burstyfile = codecs.open(args.b,"r","utf-8")
bursties = []
for line in burstyfile.readlines():
    tokens = line.strip().split("\t")
    bursties.append(tokens[0])
burstyfile.close()
bursties_set = set(bursties)
bursties_anchor = ["[[" + x + "]]" for x in bursties]
bursties_anchor_set = set(bursties_anchor)

#load in Wikipedia dump
xmldoc = minidom.parse(args.w)
pages = xmldoc.getElementsByTagName('page')

#for each page
for page in pages:
    text = page.getElementsByTagName('text')[0]
    words = text.toprettyxml().split(" ")
    #check if one of the bursty terms is present
    if bool(bursties_set & set(words)):
        matches = list(bursties_set & set(words))
        for match in matches:
            bursty_matches[match]["word"] += 1
    if bool(bursties_anchor_set & set(words)):
        matches = list(bursties_ancher_set & set(words)):
        for match in matches:
            bursty_matches[match]["anchor"] += 1

#calculate informativeness
for b in bursty_matches.keys():
    

