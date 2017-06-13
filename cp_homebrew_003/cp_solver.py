#!/usr/bin/env python
# encoding: utf-8
import sys
from time import time as now

from cp_state import State


class Solution(object):
    def __init__(self, task):
        self.best_cost = sys.maxint  # Larger than any cost, that we can take
        self.best_solution = None
        self.set_count = task.set_count
        self.proven_as_optimal = False
        self.steps = 0

    def store_result(self, state):
        if state.current_cost < self.best_cost:
            print self.steps, 'update solution to', state.current_cost  # uncomment this to see the progress
            solution = [0] * self.set_count
            state_on_stack = state
            while state_on_stack:
                for s in state_on_stack.chosen_sets:
                    solution[s] = 1
                state_on_stack = state_on_stack.parent

            self.best_solution = solution
            self.best_cost = state.current_cost

    def __repr__(self):
        return 'Solution(cost={}, optimal={}, steps={}, sets={})'.format(
            self.best_cost, self.proven_as_optimal, self.steps, self.best_solution)


def deep_search(task, timeout=10*60):
    state = State.from_task(task)
    solution = Solution(task)
    solution.metrics = state.estimator.metrics
    deadline = now() + timeout

    # Python has no tail-recursion optimization.
    # Even more, python has a limit on recursion depth
    # So, we need to write big loops iteratively

    while state:  # when we try to .negate() init state we will obtain None and will exit from the loop
        solution.steps += 1
        if not state.is_feasible:
            state = state.parent
            continue

        if state.is_all_covered():
            solution.store_result(state)
            state = state.negate()  # try to deselect the current set or rollback to the parent state
            continue

        if state.get_optimistic_cost() >= solution.best_cost:
            if now() > deadline:  # we get to this place often enough to stop in time,
                                  # and we get to it not on the each iteration, so we will not check the time too frequently
                return solution
            state = state.negate()  # try to deselect the current set or rollback to the parent state
            continue

        state = state.next_child()

    solution.proven_as_optimal = True  # we have not terminated on timeout, so we have explored all the tree
    return solution


if __name__ == '__main__':
    from reader import read_input
    for fn in ['sc_157_0', 'sc_330_0', 'sc_1000_11', 'sc_5000_1', 'sc_10000_5', 'sc_10000_2']:
        print '=== {} ==='.format(fn)
        task = read_input('sc_45_0')
        solution = deep_search(task, timeout=0.5*60)
        print solution, solution.metrics
    #from profile import run
    #run('deep_search(task, timeout=120)', sort=2)  # sort - 2 cumtime, 1 - totime
