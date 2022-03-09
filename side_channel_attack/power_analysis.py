# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 14:30:28 2022

Side-channel attack
Power analysis of AES
@author: Bence Mány, Vicente Bartual Ferran
"""

import csv
import constants
import scipy.stats

#Static variables
path_traces = "data/T3.dat"
path_inputs = "data/inputs3.dat"
s_box = constants.S
inv_s_box = constants.SI
key = 0x5b



#Reading the table of power traces
def read_traces(path_traces): 
    traces = []
    with open(path_traces, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            line = []
            for elements in row:
                line.append(float(elements))
            traces.append(line)
    return traces

    
#Calculating the Hamming-weight of a given byte
def hamming_weight(byte):
    weight = 0
    for i in (bin(byte)):
        try:
            if int(i) == 1:
                weight += 1
        except:
            continue
    return weight


#Reading the plaintext inputs
def read_inputs(path_inputs): 
    inputs = []
    with open(path_inputs, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            for elements in row:
                inputs.append(int(elements))
    return inputs
                
#Calculating the expected Hamming-weights for each input with each possible key          
def calculate_h_table(inputs):
    H_table = []
    for a in inputs:
        line = []
        for keys in range(256):
            line.append(hamming_weight(s_box[a ^ keys]))
        H_table.append(line)
    return H_table
        
        
#Calculating the Pearson correlation coefficient between the predicted and measured power traces for each possible key
def calculate_coeff():
    coeffs = []
    #Extract predictions for all keys
    for key in range(len(H_table[0])):
        
        #Extract predictions for one given key
        predicted = []
        for lines in H_table:
            predicted.append(lines[key])
        
        #Extract 55 time samples for the given key
        for i in range(len(traces[0])):
            sampled = []
            coeff_i = []
            for lines in traces:
                sampled.append(lines[i])
            coeff_i.append(scipy.stats.pearsonr(predicted, sampled)[0])
        coeffs.append(max(coeff_i))
    return coeffs
    
            
    



#Main function*****************************************************************************

traces = read_traces(path_traces)
inputs = read_inputs(path_inputs)
H_table = calculate_h_table(inputs)
coeffs = calculate_coeff()
print(H_table[0])
#print(coeffs)
#print(max(coeffs))




    


