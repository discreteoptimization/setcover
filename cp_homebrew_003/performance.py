#!/usr/bin/env python
# encoding: utf-8
from time import time as now

from reader import read_input, list_files
from validator import bruteforce_solver


def measure_duration(fn, solver=bruteforce_solver):
    start_time = now()
    solver(read_input(fn))
    return now() - start_time


def print_durations(solver=bruteforce_solver, min_task_size=0, max_task_size=20):
    for fn in list_files(min_size=min_task_size, max_size=max_task_size):
        print '{:<15}'.format(fn), '{:.4f}'.format(measure_duration(fn, solver))


if __name__ == '__main__':
    from cp_solver import deep_search
    print_durations(lambda(task): deep_search(task).best_solution, max_task_size=50)  # Put your solver and your size bounds here
