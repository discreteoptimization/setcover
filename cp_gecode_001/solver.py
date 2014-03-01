#!/usr/bin/python
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2014 Andrea Rendl
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# Pre-requisites:
#
# + Download and install Gecode: http://www.gecode.org/
#
# + Make sure that Gecode is in the LD_LIBRARY_PATH path
#   To achieve that, enter the following into your shell (or add it to your ~/.bashrc or equivalent):
#       export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/your/path/to/gecode/
#
# + compile the C++ Gecode file 'set_cover.cpp' into the executable 'set_cover' 
#   For instance, enter the following into a shell (see the script 'compile_gecode.sh'):
#       g++ -I /path/to/gecode/ -c set_cover.cpp
#       g++ -o set_cover -L /path/to/gecode/ set_cover.o -lgecodesearch -lgecodeminimodel -lgecodeint -lgecodekernel -lgecodesupport -lgecodegist -lgecodedriver

import os
from subprocess import Popen, PIPE
from collections import namedtuple

Set = namedtuple("Set", ['index', 'cost', 'items'])

def solve_it(input_data):
    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    item_count = int(parts[0])
    set_count = int(parts[1])
    
    sets = []
    for i in range(1, set_count+1):
        parts = lines[i].split()
        sets.append(Set(i-1, float(parts[0]), map(int, parts[1:])))

    # generate data file -> this is necessary since we cannot pass over the instance file name
    data_file = "data.txt"
    generateDataFile(item_count, set_count, sets, data_file)

    # specify the number of solutions you want to compute. '0' returns all solutions.
    nb_solutions = 20 

    # solve using the Gecode executable 'set_cover'
    process = Popen(['./set_cover', 'data.txt', str(nb_solutions)], 
                    stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = process.communicate()

    # comment the following line if you do not want to see Gecode's output
    print stdout
    # print error messages if there are any 
    print stderr     

    # extract the solution from standard-out
    obj,solution = extractSolution(stdout,set_count)

    # prepare the solution in the specified output format
    output_data = str(obj) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


# ##################################################################################
def generateDataFile(item_count, set_count, sets, data_file):
    tmpFile = open(data_file, 'w')
    
    out = str(item_count)+ " "+ str(set_count)+ "\n"
    for s in sets:
        out+= str(int(s.cost))
        out += " "
        for e in s.items:
            out += str(int(e)) + " "
        out += "\n"
            
    tmpFile.write(out)
    tmpFile.close()
# ##################################################################################
def extractSolution(stdout,set_count):
    solution = []
    for i in range(0, set_count):
        solution.append(0)
    
    cost = 0.0
    lines = stdout.split('\n')   
    cnt = 0
    for i in range(0,len(lines)):        
        line = lines[i]
        if line.startswith("Initial"):
            line = lines[i-3]  # move back three lines -> there is the last solution            
            words = line.split()
            cost = words[1] 
            words = lines[i-2].split()
            if len(words) != set_count:
                print "Error in number of solutions"
            else:
                for j in range(0,len(words)):
                    solution[j] = int(words[j])                
            break # we are done!
        else:
            cnt+=1
                
    return cost,solution

# ##################################################################################        
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        input_data_file = open(file_location, 'r')
        input_data = ''.join(input_data_file.readlines())
        input_data_file.close()
        print 'Solving:', file_location
        print solve_it(input_data)
    else:
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/sc_6_1)'

