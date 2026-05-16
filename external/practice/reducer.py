#!usr/bin/env python

import sys 
from collections import defaultdict

counts = defaultdict(int)

for line in sys.stdin:
    word,_ = line.strip().split("\t")
    counts[word]+=1
    
for word, cnt in counts.items():
    print(word + "\t" + str(cnt))