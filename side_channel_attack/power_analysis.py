# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 14:30:28 2022

Side-channel attack
Power analysis of AES
@author: Bence Mány, Vicente Bartual Ferran
"""

import math
from typing import List

from aes_s_box import S as S_BOX


# Data files
TRACES_FILE = "data/T3.dat"
INPUTS_FILES = "data/inputs3.dat"


def read_traces(path_traces: str) -> List[float]:
    """ Reads and parses the power traces data file.

    :param path_traces: Path to power traces file.
    :type path_traces: str

    :return: A 2-dimension list. The outer list contains 55 lists, each of them
             containing 600 values. This way, it will be easier to get the 600
             traces related to the inputs for each trace time.
    :rtype: List[List[float]]
    """
    with open(path_traces) as f:
        lines = f.readlines()

    traces = []
    for line in lines:
        input_traces = [float(t) for t in line.split(',')]
        for i in range(len(input_traces)):
            if i >= len(traces):
                traces.append([])
            traces[i].append(input_traces[i])
    return traces


def read_inputs(path_inputs: str) -> List[float]:
    """ Reads the inputs data file.

    :param path_inputs: Path to inputs file.
    :type path_inputs: str

    :return: A list containing the 600 input values.
    :rtype: List[float]
    """
    with open(path_inputs) as f:
        data = f.read()
    
    inputs = []
    for n in data.split(','):
        inputs.append(int(n))
    return inputs

    
def hamming_weight(byte: int) -> int:
    """ Calculates the Hamming Weight (number of 1 bits) of the given byte.

    :param byte: Byte from which to calculate the Hamming Weight.
    :type byte: int

    :return: The number of 1s in byte.
    :rtype: int
    """
    weight = 0
    for i in range(8):
        weight += (byte >> i) & 0x01
    return weight


def calculate_h_table(inputs: List[int]) -> List[List[int]]:
    """ Calculates the H table for the given input list. Each input value is
    xored with every possible key and then is substituted using the AES S-box.
    The final values of the H table are the Hamming Weights of those results.

    :param inputs: The input list.
    :type inputs: List[int]

    :return: A 2-dimension list. The outer list contains 256 lists (each one for
    each key, in order), and the inner lists the resulting Hamming Weights
    for its key and each input.
    :rtype: List[List[int]]
    """
    h_table = []
    for key in range(256):
        if key >= len(h_table):
            h_table.append([])
        for inp in inputs:
            h_table[key].append(hamming_weight(S_BOX[inp ^ key]))
    return h_table
        
        
def pearson_correlation(data_1: List[float], data_2: List[float]) -> float:
    """ Calculates the pearson correlation coefficient between the two input
    data sets. The data sets must have the same number of elements.

    :param data_1: First data set.
    :type data_1: List[float|int]
    :param data_2: Second data set.
    :type data_2: List[float|int]

    :return: Pearson correlation coefficient.
    :rtype: float
    """
    assert(len(data_1) == len(data_2))

    mean_1 = sum(data_1) / len(data_1)
    mean_2 = sum(data_2) / len(data_2)

    variance_1 = 0.0
    variance_2 = 0.0
    for i in range(len(data_1)):
        variance_1 += (data_1[i] - mean_1)*(data_1[i] - mean_1)
        variance_2 += (data_2[i] - mean_2)*(data_2[i] - mean_2)

    covariance = 0.0
    for i in range(len(data_1)):
        covariance += (data_1[i] - mean_1)*(data_2[i] - mean_2)
    
    return covariance / math.sqrt(variance_1*variance_2)


def key_predict(coefficients: List[List[float]]) -> tuple[float, int, int]:
    """ Finds the highest correlation for the given set of coefficients. Returns
    three values: The highest correlation, and the key and sample time that
    produced it.

    :param coefficients: The coefficients, as a 2-dimension list of all the
                         coefficients for a sample time, and for every key.
    :type: coefficients: List[List[float]]

    :return: The best coefficient and its key and sample time.
    :rtype: tuple[float, int, int]
    """
    best = 0.0
    best_key = 0
    best_sample_time = 0
    for key in range(len(coefficients)):
        for sample_time in range(len(coefficients[0])):
            if coefficients[key][sample_time] > best:
                best = coefficients[key][sample_time]
                best_key = key
                best_sample_time = sample_time
    return best, best_key, best_sample_time


def main():
    """ Main function. """
    traces = read_traces(TRACES_FILE)
    inputs = read_inputs(INPUTS_FILES)
    h_table = calculate_h_table(inputs)
    coeffs = []

    #Extract predictions for each possible key
    for key_guess in h_table:
        coeff_i = []
        for samples in traces:
            #Correlation between the key guess and the current time sample
            coeff_i.append(abs(pearson_correlation(key_guess, samples)))
        coeffs.append(coeff_i)
        
    #Determining the most likely key candidate
    correlation, key, time_sample = key_predict(coeffs)
    print(f"The most likely key candidate is 0x{key:02x} ({key})")
    print("Correlation value:", correlation)
    print("Sample time:", time_sample)


if __name__ == "__main__":
    main()
