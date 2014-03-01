#!/usr/bin/python
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2014 Carleton Coffrin
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


# This is a very simple CP style solver.
#
# It simply enumeates all combinations of the decision variables (using DFS)
# and returns the combination with the best objective value
# the function call stack is used to enumerate the search tree
#
# We will call this a "guess-and-test" solver.
# 
# This solver is not scalable, but is illustrates how to quictly prototype 
# a simple CP solver
# 

from collections import namedtuple
Problem = namedtuple("Problem", ['items', 'sets'])
Set = namedtuple("Set", ['index', 'cost', 'items'])
Solution = namedtuple("Solution", ['assignment', 'obj'])

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

    problem = Problem(range(0,item_count), sets)
    
    # define the domains of all the variables {0,1}
    domains = [range(0,2)]*set_count

    # start a trivial depth first search for a solution
    solution = tryall([], domains, problem)
    
    # prepare the solution in the specified output format
    output_data = str(solution.obj) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution.assignment))

    return output_data


def tryall(assignment, domains, problem):
    # base-case: if the domains list is empty, all values are assigned
    # check if it is a solution, return None if it is not
    if len(domains) == 0:
        obj = check_it(assignment, problem)
        if obj != None:
            return Solution(assignment, obj)
        else:
            return None
    
    # recursive-case: try each value in the next domain
    # if we find a solution return it. otherwise, try the next value
    else:
        best_sol = None
        for v in domains[0]:
            sol = tryall(assignment[:]+[v], domains[1:], problem)
            if sol != None:
                if best_sol == None or best_sol.obj > sol.obj:
                    best_sol = sol
        return best_sol

                    
# checks if an assignment is feasible,
# if so, returns the objective value
def check_it(assignment, problem):
    
    # start with all items uncovered
    covered = [0]*len(problem.items)
    obj = 0
    
    # go over the items of selected sets
    # markig covered items
    for s,v in enumerate(assignment):
        if v == 1:
            obj += problem.sets[s].cost
            for item in problem.sets[s].items:
                covered[item] = 1
                
    # if every value in covered is 1,
    # then the solution is feasible
    if sum(covered) == len(covered):
        return obj
    else:
        return None
        
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

