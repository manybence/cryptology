# -*- coding: utf-8 -*-
"""
Created on 2022/04/20

Implementation of cracking RSA by using Shor's algorithm
@author: Bence Mány, Vicente Bartual Ferran
"""

from typing import List
import math
import sympy
from random import randrange
import timeit

#Recommended maximum size = 200
size = 300

def generate_key(size: int) -> int:
    """
    Generating two unique prime numbers (the secret keys), then combining them to create the public key.

    Parameters
    ----------
    size : int
        The highest number the secret key can be.

    Returns
    -------
    int
        The public key. It has to be the product of two unique prime numbers.

    """
    p = randrange(size)
    while not sympy.isprime(p):
        p = randrange(size)
    
    q = randrange(size)
    while not (sympy.isprime(q) and not p == q):
        q = randrange(size)
        
    print("The private keys are:", p,",", q) 
    return p*q
  
 
  
def find_period(a: int, N: int) -> int:
    """
    Finds the smallest 'r' value that satisfies: (a**r)%N = 1
    This is the quantum step. It can take loooong time.

    Parameters
    ----------
    a : int
        An intermediate variable for finding good guesses.
    N : int
        The public key.

    Returns
    -------
    int
        Returns the 'r' value which is then being used to create a better guess.

    """

    r = 0
    while True:
        r += 1
        if (a**r)%N == 1:
            return r

def find_factor(N: int) -> int:
    """
    Finding the two prime factors of the given number N.

    Parameters
    ----------
    N : int
        The public key, which is the product of two unique primes.

    Returns
    -------
    int
        One of the secret keys (one of the prime factors of the given number).

    """
    factor = -1
    while True:
        try:
            a = randrange(N-2) + 2
            k = math.gcd(a, N)
            if k > 1: 
                factor = k
                break
            else:
                r = find_period(a, N)
                if r%2 > 0:
                    #Odd r value
                    continue
                else:
                    #Even r value
                    if (a**(r/2))%N == N-1:
                        continue
                    else:
                        factor = math.gcd(int(a**(r/2) + 1), N)
                        if factor > 1:
                            break
        except:
            continue
    return factor

def main():
    """ Main function. """
    
    start = timeit.default_timer()
   
    print("Generating the private and public keys")
    public_key = generate_key(size)
    print("The public key is: ", public_key)
    
    print("\nExecuting Shor's algorithm")
    factor1 = find_factor(public_key)   
    factor2 = int(public_key/factor1)
    print("Factors of", public_key," are :", factor1, ",", factor2) 
    
    end = timeit.default_timer()
    print("Time required for the attack:", round(end - start, 3), "seconds")


if __name__ == "__main__":
    main()
