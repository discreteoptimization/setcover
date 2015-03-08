#!/usr/bin/env python

"""
Simple MIP model for the set cover problem. Very hacky and completely
without error checking. This simple approach does not suffice for the
larger instances. See lns.py for a large neighborhood search based on this
model that is significantly faster.

Note that I usually just call the solver interactively, experiment
around and then manually submit the solution. Thus, there is no
automatic submit script.
"""

import sys
import os.path
import gurobipy as grb


def read(filename):
  """
  Reads a set cover instance.

  Args:
    filename: The file containing the set cover instance.

  Returns:
    A triple consisting of the instance name, the number of items n
    and the list of subsets of N := {0, ..., n - 1}. Each subset U
    is a pair of the subset cost and the list of elements in U.
  """
  with open(filename) as file:
    nitems, nsets = (int(x) for x in file.readline().split())
    sets = []
    for _ in range(nsets):
      line = file.readline().split()
      sets.append((float(line[0]), [int(x) for x in line[1:]]))
    return os.path.basename(filename), nitems, sets


def create_model(instance):
  """
  Creates a simple MIP model for a set cover instance.

  Creates one binary decision variable s_i for each set. The objective
  function is simply the sum over the c_i * s_i. The constraints
  are that each item is captured by at least one set that is taken.

  Args:
    instance: The set cover instance as created by read().

  Returns:
    A pair of the Gurobi MIP model and the mapping from the sets
    in the instance to the corresponding Gurobi variables.
  """
  name, nitems, sets = instance
  model = grb.Model(name)

  # One variable for each set. Also remember which sets cover each item.
  covered_by = [[] for i in range(nitems)]
  vars = []
  for i, set in enumerate(sets):
    cost, covers = set
    vars.append(model.addVar(obj=cost, vtype=grb.GRB.BINARY, name="s_{0}".format(i)))

    for item in covers:
      covered_by[item].append(vars[i])
  model.update()

  # Constraint: Each item covered at least once.
  for item in range(nitems):
    model.addConstr(grb.quicksum(covered_by[item]) >= 1)

  # We want to minimize. Objective coefficients already fixed during variable creation.
  model.setAttr("ModelSense", grb.GRB.MINIMIZE)

  # Tuning parameters derived from sc_330_0
  model.read("mip.prm")

  model.setParam("Threads", 3)
  model.setParam("MIPGap", 0.001)  # 0.1% usually suffices

  return model, vars


def write(model, original=True):
  """
  Writes the solution of a set cover instance to a file.

  The optimality flag will only be set if this model is still the
  original model and it states that its current solution is optimal.

  Args:
    model: The set cover MIP model as created by create_model().
    original: Is this still the original model? (default: Yes)
  """
  g_model, vars = model
  with open(g_model.getAttr("ModelName") + ".sol", "w") as file:
    file.write("{0} {1}\n".format(g_model.objval, int(original and g_model.status == grb.GRB.status.OPTIMAL)))
    for var in vars:
      file.write("{0} ".format(int(var.x)))
    file.write("\n")

if __name__ == "__main__":
  instance = read(sys.argv[1])
  model = create_model(instance)
  model[0].optimize()
  write(model)
