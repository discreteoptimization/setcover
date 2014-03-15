#!/usr/bin/env python

"""Simple MIP model for the set cover problem.

This solution is very hacky and does not contain any error checking.

Note that I usually just call the solver interactively, experiment
around and then manually submit the solution. Thus, there is no
automatic submit script."""

import sys
import os.path
import gurobipy as grb


def read(filename):
  """Read a set cover instance.

  Output:
  A triple consisting of the instance name, the number of items n
  and the list of subsets of N := {0, ..., n-1}. Each subset U
  is a pair of the subset cost and the list of elements in U.
  """
  with open(filename) as file:
    nitems, nsets = (int(x) for x in file.readline().split())
    sets = []
    for i in range(nsets):
      line = file.readline().split()
      sets.append((float(line[0]), [int(x) for x in line[1:]]))
    return os.path.basename(filename), nitems, sets


def create_model(instance):
  """Create a simple MIP model for a set cover instance.

  Output:
  Pair of Gurobi MIP model and a mapping from the sets
  to the corresponding Gurobi variables.

  Approach:
  One binary decision variable s_i for each set. The objective
  function is simply the sum over the c_i * s_i. The constraints
  are that each item is captured by at least set that is taken.
  """
  name, nitems, sets = instance
  model = grb.Model(name)

  # One variable for each set, also remember which sets cover each item
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

  # Objective coefficients already fixed during variable
  # declaration. So just state that we want to minimize.
  model.setAttr("ModelSense", grb.GRB.MINIMIZE)

  return model, vars


def solve(model, timelimit=float('inf'), first=True):
  """Solve a set cover MIP instance.

  Basically just calls the Gurobi solver with some
  nice parameters.
  """
  g_model = model[0]

  # Only set parameters on first call -> avoids massive console output
  if first:
    # Tuning parameters derived from sc_330_0
    g_model.read("mip.prm")

    g_model.setParam("Threads", 3)
    g_model.setParam("MIPGap", 0.001)  # 0.1% suffices
    g_model.setParam("TimeLimit", timelimit)

    # If you are out of memory this may be useful:
    # g_model.setParam("Threads", 1)
    # g_model.setParam("NodefileStart", 4.0)

  g_model.optimize()


def write(model):
  """Write the solution of a set cover instance to a file."""
  g_model, vars = model
  with open(g_model.getAttr("ModelName") + ".sol", "w") as file:
    file.write("{0} {1}\n".format(
        g_model.objval, int(g_model.status == grb.GRB.status.OPTIMAL)))
    for var in vars:
      file.write("{0} ".format(int(var.x)))
    file.write("\n")

if __name__ == "__main__":
  instance = read(sys.argv[1])
  model = create_model(instance)
  solve(model)
  write(model)
