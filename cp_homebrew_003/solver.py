#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
The MIT License (MIT)
Copyright (c) 2017 Yuri Kovalev

This CP solver can find the optimal solution on small datasets (until sc_45_0)
For greater datasets there is a timeout option. After timeout it stops searching and submits best found solution.
In practice, the solver only takes a few minutes to get 7/10 scores for all tasks in the assignment.
Further search is not so productive and does not improve solutions significantly.
"""

import sys
from reader import parse_input
from cp_solver import deep_search


def solve_it(input_data, timeout=10*60):
    task = parse_input(input_data)
    solution = deep_search(task, timeout)
    # prepare the solution in the specified output format
    return '{} {}\n{}'.format(int(solution.best_cost),          # from float
                              int(solution.proven_as_optimal),  # from boolean
                              ' '.join(map(str, solution.best_solution))  # from list of int
                              )

if __name__ == '__main__':
    file_location = '../data/sc_6_1'
    timeout = 10*60
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        if len(sys.argv) > 2:
            timeout = int(sys.argv[2].strip())

    input_data_file = open(file_location, 'r')
    input_data = ''.join(input_data_file.readlines())
    input_data_file.close()
    print 'Solving:', file_location
    print solve_it(input_data, timeout)

