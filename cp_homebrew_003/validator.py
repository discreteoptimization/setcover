#!/usr/bin/env python
# encoding: utf-8
"""
For local testing purposes
"""
from itertools import compress, chain, product, ifilter
from functools import partial

from reader import read_input, list_files


def is_valid(task, solution):
    """
    :param reader.Task task:
    :param list[1|0] solution:
    :return bool: whether constraints in task are met
    """
    sets = compress(task.sets, solution)
    items_covered = set(chain.from_iterable(s.items for s in sets))
    return len(items_covered) == task.item_count


def calc_cost(task, solution):
    """
    :param reader.Task task:
    :param list[1|0] solution:
    :return int:
    """
    sets = compress(task.sets, solution)
    return sum(s.cost for s in sets)


def bruteforce_solver(task):
    """
    As simple solution as we can make.
    It finds the optimal solution, but it can't work on big inputs
     (say, 20 sets take a few seconds, 25 sets - take a few minutes)
    :param reader.Task task:
    :return list[1|0]:
    """
    all_configurations = product([0, 1], repeat=task.set_count)

    valid_configurations = ifilter(partial(is_valid, task), all_configurations)

    return min(valid_configurations, key=partial(calc_cost, task))


def check_solver(solver, inputs=list_files(max_size=20)):
    """
    Prove optimality with comparing solution with control version.
    Only for small examples, sorry. For big ones you can call is_valid()
    :param task:
    :param function(task) solver:
    :return:
    """
    for fn in inputs:
        task = read_input(fn)
        solution = solver(task)

        if not is_valid(task, solution):
            print 'ERROR: solution for {fn} is invalid: {solution}'.format(fn=fn, solution=solution)
            continue

        control_solution = bruteforce_solver(task)
        control_cost = calc_cost(task, control_solution)
        cost = calc_cost(task, solution)
        if cost != control_cost:
            msg = ('ERROR: solution for {fn} has cost={cost}, but optimal is {control_cost}:\n' +
                   '    control:{control_solution}\n' +
                   '    tested: {solution}')
            print msg.format(fn=fn, cost=cost, control_cost=control_cost,
                             control_solution=control_solution, solution=solution)
            continue

        print 'OK: solution for {fn} is optimal, cost={cost}'.format(fn=fn, cost=cost)


if __name__ == '__main__':
    from cp_solver import deep_search
    check_solver(lambda (task): deep_search(task).best_solution)  # put your solver here
    # check_solver(lambda (task): deep_search(task).best_solution, list_files(min_size=30, max_size=50))  # put your solver here
