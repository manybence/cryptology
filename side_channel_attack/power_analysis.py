# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 14:30:28 2022

Side-channel attack
Power analysis of AES
@author: Bence Mány, Vicente Bartual Ferran
"""

import csv
import math
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
def corr(h_values, t_values):
    assert(len(h_values) == len(t_values))
    assert(len(h_values) == 600)

    h_avg = sum(h_values) / len(h_values)
    t_avg = sum(t_values) / len(t_values)

    h_var = 0.0
    t_var = 0.0
    for i in range(len(h_values)):
        h_var += (h_values[i] - h_avg)*(h_values[i] - h_avg)
        t_var += (t_values[i] - t_avg)*(t_values[i] - t_avg)
    den = math.sqrt(h_var*t_var)

    corr = 0.0
    for i in range(len(h_values)):
        corr += (h_values[i]-h_avg)*(t_values[i]-t_avg)
    corr /= den
    return corr


#Finding the highest correlation among possible key values. 
#The function assumes that the "coeffs" input stores the related coefficient values in an ordered list.
def key_predict(coeffs):
    best = 0
    key_pred = 0
    num = 0
    for i in coeffs:
        if max(i) > best:
            best = max(i)
            key_pred = num
        num += 1
    return key_pred, best


#Main function*****************************************************************************

def main():
    traces = read_traces(path_traces)
    inputs = read_inputs(path_inputs)
    H_table = calculate_h_table(inputs)
    coeffs = []

    #Extract predictions for each possible key
    for key in range(len(H_table[0])):        
        predicted_i = []
        for lines in H_table:
            predicted_i.append(lines[key])    
        #Extract each time samples for the given key
        coeff_i = []
        for i in range(len(traces[0])):
            sampled = []
            for lines in traces:
                sampled.append(lines[i])        
            #Calculate correlation between the prediction and the current time sample
            #coeff_i.append(scipy.stats.pearsonr(predicted_i, sampled)[0])
            coeff_i.append(corr(predicted_i, sampled))
        coeffs.append(coeff_i)
        
    #Determining the most likely key candidate
    key, correlation = key_predict(coeffs)
    print("The most likely key is: ", key, "\nwith the correlation value: ", correlation)




if __name__ == "__main__":
    main()
            




    


