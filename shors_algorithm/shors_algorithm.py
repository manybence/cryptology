# -*- coding: utf-8 -*-
"""
Created on 2022/04/20

Implementation of Shor's algorithm
@author: Bence Mány, Vicente Bartual Ferran
"""

from typing import List
import math
from random import randrange

def period(a, N):
    "Finds the smallest 'r' value that satisfies: a**r mod(N) = 1"
    for r in range(1, N):
        if (a**r)%N == 1:
            return r
    return 0

def find_factors(N: int):
    k = 0
    while k<=1:
        a = randrange(N)
        print("a = ", a)
        k = math.gcd(a, N)
        print("k = ", k)
    return

def main():
    """ Main function. """
    N = 10
    find_factors(N)


if __name__ == "__main__":
    main()
