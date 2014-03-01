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


# This is a simple CP style solver, with enhancements byond the guest-and-test
# solver in cp_homebrew_001.
# 
# Enchancements Include:
# - Maintianing a best-found solution during search
# - Puring nodes using a "bounding" routing (i.e. branch-and-bound)
# - Filtering variable domains via simple routines 
# - Comments indicating directions for further improvements
# 
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
    
    
    # Improvement: re-order sets from the order in the file 
    #  to improve the search procudure.
    #  Don't forget to un-order them in the output_data.
    problem = Problem(range(0,item_count), sets)
    
    solver_data = {'best_solution':None, 'node_count':0, 'fail_count':0}
    
    # define the domains of all the variables {0,1}
    domains = [range(0,2)]*set_count
    
    # start a trivial depth first search for a solution
    tryall([], domains, problem, solver_data)
    
    solution = solver_data['best_solution']
    
    print 'total search nodes:', solver_data['node_count']
    print 'total fails:       ', solver_data['fail_count']
    
    # prepare the solution in the specified output format
    output_data = str(solution.obj) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution.assignment))
    
    return output_data


def tryall(assignment, domains, problem, data):
    data['node_count'] += 1
    
    # base-case: if the domains list is empty, all values are assigned
    # check if it is a feasible solution,
    # if feasible, check if it is the best found solution so far
    # if so, up date the best the found solution 
    if len(domains) == 0:
        obj = check_it(assignment, problem)
        if obj != None:
            if data['best_solution'] == None or data['best_solution'].obj > obj:
                print 'improved solution to:', obj, ' \tsearch nodes:', data['node_count'], ' \tfails:', data['fail_count'] 
                data['best_solution'] = Solution(assignment, obj)
            else:
                data['fail_count'] += 1
        return
    
    
    # *** Filtering Routine ***
    # The following code has three functions,
    # 1 - check if the remaining subtree has a feasible solution
    # 2 - detect if any sets *must* to be taken, in the remaining subtree
    # 3 - detect if any sets *need not* be taken, in the remaining subtree
    covered_so_far = [0]*len(problem.items)
    for s,v in enumerate(assignment):
        if v == 1:
            for item in problem.sets[s].items:
                covered_so_far[item] = 1

    remaining_sets = range(len(assignment), len(assignment)+len(domains))
    
    #for each item, which of the remaining sets can cover it
    sets_that_cover = []
    
    for item in problem.items:
        sets_that_cover.append(set())
    
    for s in remaining_sets:
        for item in problem.sets[s].items:
            sets_that_cover[item].add(s)
    
    for item in problem.items:
        if covered_so_far[item] == 0:
            # if we have not covered an item and
            # no remaing sets can conver that item
            # then the remaining subtree contains no feasible solution
            if len(sets_that_cover[item]) == 0:
                data['fail_count'] += 1
                return None
        
            # if we have not covered an item and
            # exactly one remaing set can conver that item
            # then we must take that set in the remaining subtree
            if len(sets_that_cover[item]) == 1:
                for s in sets_that_cover[item]:
                    domains[s-len(assignment)] = [1]
    
    for s in remaining_sets:
        covered_count = sum([covered_so_far[item] for item in problem.sets[s].items])
        
        # assuming all costs are posative:
        # if every item in a set is already covered
        # taking that set can only increase the objective value
        # hence, we need not consider adding that set in the remaining subtree
        if covered_count == len(problem.sets[s].items):
            domains[s-len(assignment)] = [0]
    
    
    
    # *** Bounding Routine ***
    # it checks if this the partial assignment is worse than the best solution
    # we have found so far, if so, we can stop
    # 
    # Improvement: use the domains of the variables to improve this bound.
    cost_so_far = sum([problem.sets[i].cost for i,v in enumerate(assignment) if v == 1])
    if data['best_solution'] != None and cost_so_far >= data['best_solution'].obj:
        data['fail_count'] += 1
        return None


    # *** Exploration to Try ***
    #
    # Try running this solver on a small data set (e.g. sc_6_1)
    # and comment out components of the bounding and filtering routines
    # observe how the search procedure and number of nodes is effected.
    #
    
    
    # *** Improvements to Consider ***
    # 
    # 1) Add a time limit to the solver, so it can be used on larger instances.
    # 
    # 2) Both the bounding and filtering routines are linear time computations,
    #    in the worst case, can you make them constant time?
    #
    # 3) Add a new filtering rule(s) that removes sets which are "donminated" by 
    #    other sets.  For example if set A is a sub-set of set B and
    #    set A is more costly than set B, then set A can be removed. 
    #    (i.e. it's domain set to [0])
    #
    # 4) Currintly the filtering only runs once, however any deductions made
    #    in a single filtering step could lead to more deductions.
    #    Extend the filtering to iterate until a fixpoint is reached.
    #
    
    # recursive-case: try each value in the next domain
    for v in domains[0]:
        tryall(assignment[:]+[v], domains[1:], problem, data)
        
    return


                
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

