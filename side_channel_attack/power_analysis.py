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


#Global variables
traces = []
inputs = []
H_table =[]



#Reading the table of power traces
def read_traces(): 
    with open(path_traces, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            line = []
            for elements in row:
                line.append(float(elements))
            traces.append(line)

    
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
def read_inputs(): 
    with open(path_inputs, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            for elements in row:
                inputs.append(int(elements))
                
#Calculating the expected Hamming-weights for each input with each possible key          
def calculate_h_table():
    for a in inputs:
        line = []
        for keys in range(256):
            line.append(hamming_weight(s_box[a ^ keys]))
        H_table.append(line)
        
        
#Calculating the Pearson correlation coefficient between the predicted and measured power traces for each possible key
def calculate_coeff():
    predicted = []
    sampled = []
    coeff = []
    for lines in H_table:
        predicted.append(lines[0])
    for lines in traces:
        sampled.append(lines[0])
    coeff = scipy.stats.pearsonr(predicted, sampled)[0]
    print(coeff)
            
    



#Main function*****************************************************************************

read_traces()
read_inputs()
calculate_h_table()
calculate_coeff()



    


