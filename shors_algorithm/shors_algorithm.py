# -*- coding: utf-8 -*-
"""
Created on 2022/04/20

Implementation of cracking RSA by using Shor's algorithm
@author: Bence Mány, Vicente Bartual Ferran
"""

import sys
import math
import sympy
from random import randrange
import timeit
import matplotlib.pyplot as plt


def generate_keys(key_size: int) -> "tuple[int, int, int]":
    """
    Generating two unique prime numbers (the secret keys), then combining them
    to create the public key.

    Parameters
    ----------
    size : int
        The size of the public key (in bits). RSA uses 1028 bits, but that would
        be uncrackable by a normal computer. Recommended value is max 60.

    Returns
    -------
    tuple[int, int, int]
        It returns three values: n, the product of the prime numbers; e, the
        encryption exponent and d, the decryption exponent.
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
        sys.exit(1)


def calculate_e_and_d(p: int, q: int) -> "tuple[int, int]":
    """
    Calculates the RSA numbers e and d, part of the public and private key
    respectively.

    Parameters
    ----------
    p : int
        The first prime number.
    q: int
        The second prime number.

    Returns
    -------
    tuple[int, int]
        It returns two values: e, the encryption exponent and d, the decryption
        exponent.
    """
    totient_n = math.lcm(p-1, q-1)

    # e has to be coprime with the totient of n
    e = 3
    while True:
        if sympy.isprime(e) and math.gcd(totient_n, e) == 1:
            break
        e += 1

    # d is calculated as the multiplicative inverse of e
    d = 0
    x1 = 0
    x2 = 1
    y1 = 1
    temp_e = e
    temp_totient = totient_n

    while temp_e > 0:
        temp1 = temp_totient//temp_e
        temp2 = temp_totient - temp1*e
        temp_totient = temp_e
        temp_e = temp2

        x = x2 - temp1 * x1
        y = d - temp1 * y1

        x2 = x1
        x1 = x
        d = y1
        y1 = y

    if temp_totient == 1:
        d += totient_n
    return e, d


def brute_force(n: int) -> "tuple[int, int]":
    """
    Finds the two prime factors of the given number n by brute force.

    Parameters
    ----------
    n : int
        The number to be factorized. It is the product of two unique primes.

    Returns
    -------
    tuple[int,int]
        The number's two prime factors.
    """
    for i in range(2, n):
        if n % i == 0:
            return i, n//1
  

def find_period(a: int, n: int) -> int:
    """
    Finds the smallest 't' value that satisfies: (a**t)%N = 1.
    This is the quantum step. In a regular computer, it takes a long time.

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
        if (a**t) % n == 1:
            return t
        if t % 50000 == 0:
            # If t grows higher than 50000, try with another base a.
            # In our experiments, this has proven faster than just keep trying
            # with the same base, increasing t.
            return 1


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
        a += 1
        print(f"Trying new 'a' value ({a})")
        k = math.gcd(a, n)
        if k != 1: 
            factor = k
            break
        else:
            t = find_period(a, n)
            if t % 2 > 0:
                continue
            elif (a**(t//2)) % n == n-1:
                continue
            else:
                factor = math.gcd(a**(t//2)+1, n)
                if factor > 1:
                    break
    return factor, int(n/factor)


AVERAGE = 5 # Times run for each key size

def main():
    """ Main function. """
    
    times_shor = []
    times_bf = []
    sizes = []

    for i in range(4, 21, 2):
        time_shor_avg = 0
        time_bf_avg = 0
        sizes.append(i)
        for _ in range(AVERAGE):
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
            time_bf_avg += end - start
            
            print("\nExecuting Shor's algorithm")
            start = timeit.default_timer()
            factor1, factor2 = shors_algorithm(n)  
            _, d = calculate_e_and_d(factor1, factor2)
            print("The private key (n, d) is ({n}, {d})")
            end = timeit.default_timer() 
            print("Processing time:", round(end - start, 6), "seconds")
            time_shor_avg += end - start
        times_shor.append(time_shor_avg/AVERAGE)
        times_bf.append(time_bf_avg/AVERAGE)
        
    plt.plot(sizes, times_shor, label = "Shor's alg.")
    plt.plot(sizes, times_bf, label = "Brute-force")
    plt.ylabel('Processing time [s]')
    plt.xlabel('Key size [bits]')
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
