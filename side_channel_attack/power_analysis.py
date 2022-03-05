# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 14:30:28 2022

PRESENT S-box power consuption analysis
@author: Bence Mány
"""
import random

def hw(number):
    weight = 0
    for i in (bin(number)):
        try:
            if int(i) == 1:
                weight += 1
        except:
            continue
    return weight

key = 0xb
S_box = [0xc, 0x5, 0x6, 0xb, 0x9, 0x0, 0xa, 0xd, 0x3, 0xe, 0xf, 0x8, 0x4, 0x7, 0x1, 0x2]
traces = []

random.seed()

for i in range(50):
    plain = int(random.random()*15)
    x = key ^ plain
    out = S_box[x]
    traces.append(hw(out))
    
print(traces)

