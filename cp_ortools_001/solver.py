#!/usr/bin/python
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2014 Carleton Coffrin
#
#solve problem using Constraint Programming Solvers - ortools, which is an open source and provide Python apis
#install ortools: for Python 2.7 or 3.5+ installed:
#python -m pip install --upgrade --user ortools

import time
from collections import namedtuple, defaultdict
from ortools_solver import solver

Set = namedtuple("Set", ['index', 'cost', 'items'])

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    item_count = int(parts[0])
    set_count = int(parts[1])
    
    sets = []
    for i in range(1, set_count+1):
        parts = lines[i].split()
        sets.append(Set(i-1, float(parts[0]), set(map(int, parts[1:]))))

    #ortools
    obj, is_optimal, solution = solver(set_count, item_count, sets, max_minutes=10)

    output_data = str(obj) + ' ' + str(is_optimal) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        result = solve_it(input_data)
        print(result)
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/sc_6_1)')

