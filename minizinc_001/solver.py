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
# + Download and install Minizinc: http://www.minizinc.org/
# + Make sure that the Minizinc binaries are part of your PATH
# + If you want to use mzn-gecode, install Gecode: http://www.gecode.org

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

    # generate MiniZinc data file
    data_file = "data.dzn"
    generateMinizincDataFile(item_count, set_count, sets, data_file)

    # solve with Minizinc's MIP solver
    process = Popen(['mzn-g12mip', 'setCovering.mzn', 'data.dzn'],
                    stdout=PIPE, stderr=PIPE)
    # alternatively solve with Minizinc's CP solver, Gecode
    #process = Popen(['mzn-gecode', 'setCovering.mzn', 'data.dzn'],
    #                stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = process.communicate()

    # print error messages if there are any 
    print stderr
    # extract the solution from standard-out
    solution = extractSolution(stdout,set_count)

    # calculate the cost of the solution
    obj = sum([s.cost*solution[s.index] for s in sets])

    # prepare the solution in the specified output format
    output_data = str(obj) + ' ' + str(1) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


# ##################################################################################
def generateMinizincDataFile(item_count, set_count, sets, data_file):
    tmpFile = open(data_file, 'w')
    
    out = "% automatically generated Minizinc data file\n"
    out += "nbItems = " + str(item_count)+ ";\n"
    out += "nbSets = " + str(set_count)+ ";\n"
    out += "weights = [ " 
    cnt = 0
    for s in sets: 
        out += str(int(s.cost))
        if cnt == len(sets)-1:
            out += "];\n"
        else: 
            out += ", "
        cnt += 1
    out += "sets = [ "
    cnt = 0
    for s in sets:
        out += " { "
        cnt2 = 0
        for e in s.items:
            out += str(int(e))
            if cnt2 == len(s.items)-1:
                out+=" }"
            else:
                out+= ", "
            cnt2 += 1

        if cnt == len(sets)-1:
            out += " ];\n"
        else:
            out += ", "
        cnt += 1
    tmpFile.write(out)
    tmpFile.close()
# ##################################################################################
def extractSolution(stdout,set_count):
    solution = []
    for i in range(0, set_count):
        solution.append(0)
    
    lines = stdout.split('\n')   
    line = lines[0]
    words = line.split()
    if len(words) != set_count:
        print "Error in number of solutions"
    else:
        for i in range(0,len(words)):
            solution[i] = int(words[i])

    return solution

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

