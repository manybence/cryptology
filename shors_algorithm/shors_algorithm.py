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

        e, d = calculate_e_and_d(p, q)
            
        print(f"The prime factors are {p} and {q}")
        print(f"The public key (n,e) is ({n},{e})")
        print(f"The private key (n,d) is ({n},{d})")
        return n, e, d
    else:
        print("Incorrect key size. It has to be at least 4 bits.")
        return -1


def calculate_e_and_d(p: int, q) -> tuple[int, int]:
    totient_func = math.lcm(p-1, q-1)
    e = 3
    while True:
        if sympy.isprime(e) and math.gcd(totient_func, e) == 1:
            break
        e += 1
    d = multiplicative_inverse(e, totient_func)
    return e, d


def multiplicative_inverse(e, phi):
    d = 0
    x1 = 0
    x2 = 1
    y1 = 1
    temp_phi = phi

    while e > 0:
        temp1 = temp_phi//e
        temp2 = temp_phi - temp1*e
        temp_phi = e
        e = temp2

        x = x2 - temp1 * x1
        y = d - temp1 * y1

        x2 = x1
        x1 = x
        d = y1
        y1 = y

    if temp_phi == 1:
        return d + phi

  
def brute_force(n: int) -> tuple[int, int]:
    """
    Finds the two prime factors of the given number n by brute force.

    Parameters
    ----------
    n : int
        The number which needs to be factorized. It is the product of two unique primes.

    Returns
    -------
    tuple[int,int]
        The number's two prime factors.
    """
    for i in range(2, n):
        if n % i == 0:
            return i, int(n/1)
    print("ERROR!")
  

def find_period(a: int, n: int) -> int:
    """
    Finds the smallest 't' value that satisfies: (a**t)%N = 1
    This is the quantum step. It can take loooong time.

    Parameters
    ----------
    a : int
        An intermediate variable for finding good guesses.
    n : int
        The number to be factorized.

    Returns
    -------
    int
        Returns the 't' value which is then being used to create a better guess.

    """
    t = 0
    print("Searching for period...")
    while True:
        t += 1
        if (a**t)%n == 1:
            return t


def shors_algorithm(n: int) -> int:
    """
    Finds the two prime factors of the given number N using Shor's algorithm.

    Parameters
    ----------
    n : int
        The number to be factorized. It is the product of two unique primes.

    Returns
    -------
    int
        The number's two prime factors.
    """
    a = 1
    while True:
        #a = randrange(n-2) + 2
        a += 1
        print(f"Trying new 'a' value ({a})")
        k = math.gcd(a, n)
        if k > 1: 
            factor = k
            break
        else:
            t = find_period(a, n)
            print(t)
            if t%2 > 0:
                continue
            elif (a**(t/2))%n == n-1:
                continue
            else:
                factor = math.gcd(int(a**(t/2) + 1), n)
                if factor > 1:
                    break
    return factor, int(n/factor)

def main():
    """ Main function. """
    
    times_shor = []
    times_bf = []
    sizes = []
    #Recommended range: (4, 19)
    for i in range(4, 17):
        if i%2 == 0:
            sizes.append(i)
            
            print("\n\nGenerating the private and public keys")
            print(f"Key size: {i}")
            n, e, d = generate_keys(i)
            
            print("\nExecuting brute force attack")
            start = timeit.default_timer()
            factor1, factor2 = brute_force(n)
            _, d = calculate_e_and_d(factor1, factor2)
            print("The private key (n, d) is ({n}, {d})")
            end = timeit.default_timer()
            print("Processing time:", round(end - start, 6), "seconds")
            times_bf.append(round(end - start, 6))
            
            print("\nExecuting Shor's algorithm")
            start = timeit.default_timer()
            factor1, factor2 = shors_algorithm(n)  
            _, d = calculate_e_and_d(factor1, factor2)
            print("The private key (n, d) is ({n}, {d})")
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
