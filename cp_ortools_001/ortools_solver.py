#!/usr/bin/python
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2019 Qi Wang

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from ortools.sat.python import cp_model
import time
from collections import namedtuple, defaultdict

Set = namedtuple("Set", ['index', 'cost', 'items'])
import sys
import numpy as np



def reader(input_data):
    lines = input_data.split('\n')

    parts = lines[0].split()
    item_count = int(parts[0])
    set_count = int(parts[1])

    sets = []
    for i in range(1, set_count+1):
        parts = lines[i].split()
        sets.append(Set(i-1, float(parts[0]), set(map(int, parts[1:]))))
    return sets, item_count, set_count

# You need to subclass the cp_model.CpSolverSolutionCallback class.
class VarArrayAndObjectiveSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0
        self.start = time.time()
        self.start_interval = time.time()

    def on_solution_callback(self):
        t1 = time.time()
        time_used = t1 - self.start
        interval_used = t1 - self.start_interval
        self.start_interval = t1
        print('Interval using %.4f, Accu using %.4f, Solution %i' % (interval_used, time_used, self.__solution_count), end = ', ')
        print('objective value = %i' % self.ObjectiveValue())
        #for v in self.__variables:
        #    print('  %s = %i' % (v, self.Value(v)), end=',')
        #print()
        self.__solution_count += 1

    def solution_count(self):
        return self.__solution_count


def solver(set_count, item_count, sets, max_minutes=10):
    setrange = range(set_count)
    itemrange = range(item_count)
    have_item = np.zeros([set_count, item_count], dtype ='int')
    cost = [int(s.cost) for s in sets]
    max_cost = sum(cost)

    # Creates the model.
    model = cp_model.CpModel()

    # Creates the variables.
    x = [0]*set_count
    for s in setrange:
        for i in sets[s].items:
            have_item[s,i] = 1
    for s in setrange:
        x[s] = model.NewBoolVar('x%s'%(s))

    # Creates the constraints.
    for i in itemrange: 
        model.Add(sum(have_item[s][i]*x[s] for s in setrange) >= 1)

    # Creates the objective,    
    model.Minimize(sum(cost[s]*x[s] for s in setrange))

    # Creates a solver and solves.
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60*max_minutes
    solution_printer = VarArrayAndObjectiveSolutionPrinter(x)
    status = solver.SolveWithSolutionCallback(model, solution_printer)
    print('----------------')
    print('Status       : %s' % solver.StatusName(status))
    print('#sol found   : %i' % solution_printer.solution_count())
    print('Branches     : %i' % solver.NumBranches())
    print('Wall time    : %f s' % solver.WallTime())

    obj = solver.ObjectiveValue()
    solution = [0]*set_count
    for idx, xi in enumerate(x):
        solution[idx] = solver.Value(xi)
    is_optimal = -1
    if status == cp_model.OPTIMAL:
        is_optimal = 1
    elif status == cp_model.FEASIBLE:
        is_optimal = 0
    print('Obj          : %s' %(obj))
    print('Solution     : %s' %(','.join(map(str, solution))))
    print('----------------')
    return obj, is_optimal, solution

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
            sets, item_count, set_count = reader(input_data)
    obj, is_optimal, solution = solver(set_count, item_count, sets, max_minutes=1)
