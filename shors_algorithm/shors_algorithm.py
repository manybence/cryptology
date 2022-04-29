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
import matplotlib.pyplot as plt


#TODO: Simulation for different key sizes -> time elapsed - Brute-force vs Shor's
#TODO: Proper RSA encryption?
#TODO: Proper key generation
#TODO: Smarter brute force attack? Storing prime numbers?

#RSA key size = 1028 bit
#Recommended maximum size = 20 bit
key_size = 18

def generate_keys(key_size: int) -> int:
    """
    Generating two unique prime numbers (the secret keys), then combining them to create the public key.

    Parameters
    ----------
    size : int
        The size of the public key (in bits). RSA uses 1028 bits, but that would be uncrackable by a normal computer. Recommended value is max 60.

    Returns
    -------
    int
        The generated public key, which is the product of the two private keys.

    """
    if key_size >= 4:
        size = 2**int(key_size/2)
        
        p = randrange(size)
        while not sympy.isprime(p):
            p = randrange(size)
        
        q = randrange(size)
        while not (sympy.isprime(q) and not p == q):
            q = randrange(size)
            
        n = p*q
        
        #l = math.lcm(p-1, q-1)
            
        print("The private keys are:", p,",", q) 
        return p*q
    else:
        print("Incorrect key size. It has to be at least 4 bits.")
        return -1
  
def brute_force(public_key: int) -> List[int]:
    """
    Brute force attack to crack RSA.

    Parameters
    ----------
    public_key : int
        The public key which needs to be cracked. It is the product of two unique primes.

    Returns
    -------
    List[int]
        The two private keys.

    """
    
    for i in range(2, public_key):
        if public_key % i == 0:
            keys = [i, int(public_key/i)]
            return keys
  
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
    print("Searching for period...")
    while True:
        r += 1
        if (a**r)%N == 1:
            return r

def shors_algorithm(N: int) -> int:
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
    while True:
        try:
            a = randrange(N-2) + 2
            print("Trying new 'a' value")
            k = math.gcd(a, N)
            if k > 1: 
                factor = k
                break
            else:
                r = find_period(a, N)
                if r%2 > 0:
                    continue
                else:
                    if (a**(r/2))%N == N-1:
                        continue
                    else:
                        factor = math.gcd(int(a**(r/2) + 1), N)
                        if factor > 1:
                            break
        except:
            continue
    return [factor, int(N/factor)]

def main():
    """ Main function. """
    
    times_shor = []
    times_bf = []
    sizes = []
    #Recommended range: (4, 19)
    for i in range(4, 23):
        if i%2 == 0:
            sizes.append(i)
            
            print("\n\nGenerating the private and public keys")
            public_key = generate_keys(i)
            print("The public key is: ", public_key)
            
            print("\nExecuting brute force attack")
            start = timeit.default_timer()
            factor1, factor2 = brute_force(public_key)
            print("The private keys are:", factor1, ",", factor2)
            end = timeit.default_timer()
            print("Processing time:", round(end - start, 6), "seconds")
            times_bf.append(round(end - start, 6))
            
            print("\nExecuting Shor's algorithm")
            start = timeit.default_timer()
            factor1, factor2 = shors_algorithm(public_key)  
            print("The private keys are:", factor1, ",", factor2)
            end = timeit.default_timer() 
            print("Processing time:", round(end - start, 6), "seconds")
            times_shor.append(round(end - start, 6))
        
    plt.plot(sizes, times_shor, label = "Shor's alg.")
    plt.plot(sizes, times_bf, label = "Brute-force")
    plt.ylabel('Processing time [s]')
    plt.xlabel('Key size [bits]')
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
