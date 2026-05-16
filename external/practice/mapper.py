#!usr/bin/env python

import sys, re

for line in sys.stdin:
    for word in re.split(r"[,\s]+", line.lower().split()):
        if word:
            print(word + "\t1")