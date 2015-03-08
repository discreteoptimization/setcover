#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Large neighborhood search for set cover based on a MIP solver.

Includes an adaptive neighborhood size.
"""

import random
import sys
import gurobipy as grb
import mip as m

def large_neighborhood(model):
  """
  Solves a set cover instance with large-neighborhood search.

  In each call to the MIP solver we exclude a fixed ratio of the sets that
  are currently unused.

  Args:
    model: The set cover MIP model as created by mip.create_model().
  """
  # Time limit per MIP call in s
  TIMELIMIT = 3
  # Ratio of unused nodes to exclude
  FIX_RATIO = 0.9
  
  SAMPLE_SIZE = 30
  FEASIBLE_COUNT = 0
  INFEASIBLE_COUNT = 0


  g_model, vars = model
  g_model.setParam("OutputFlag", 0)
  g_model.setParam("TimeLimit", len(vars)*0.05)

  print("Processing " + g_model.getAttr("ModelName"))

  # Warmup
  g_model.optimize()
  print("Initial solution: {0}".format(g_model.objval))
  m.write(model)
  #g_model.setParam("SolutionLimit", 2147483647)
  g_model.setParam("TimeLimit", TIMELIMIT)
  
  best_obj = g_model.objval
  best_sol = {var:int(var.x) for var in vars}
  obj_constraint = g_model.addConstr(g_model.getObjective() <= best_obj - 1)
  
  if g_model.status != grb.GRB.OPTIMAL:
    while g_model.status != grb.GRB.INTERRUPTED:
      # Add the additional constraints as described above
      added_constraints = []
      for var in vars:
        if best_sol[var] == 0 and random.random() < FIX_RATIO:
          added_constraints.append(g_model.addConstr(var == best_sol[var]))

      g_model.optimize()

      # Remove the additional constraints again
      for constraint in added_constraints:
        g_model.remove(constraint)

      #print g_model.status
      if g_model.status != grb.GRB.INFEASIBLE:
        FEASIBLE_COUNT += 1;
        if g_model.objval < best_obj:
          sys.stdout.write("\nNext solution:    {0}\n".format(g_model.objval))
          m.write(model, False)

          best_obj = g_model.objval
          best_sol = {var:int(var.x) for var in vars}

          g_model.remove(obj_constraint)
          obj_constraint = g_model.addConstr(g_model.getObjective() <= best_obj - 1)

          FEASIBLE_COUNT = 0
          INFEASIBLE_COUNT = 0
        else:
          sys.stdout.write('_')
      else:
        INFEASIBLE_COUNT += 1;
        sys.stdout.write('.')
        sys.stdout.flush()

      if (FEASIBLE_COUNT+INFEASIBLE_COUNT) == SAMPLE_SIZE:
        if FEASIBLE_COUNT > SAMPLE_SIZE * 0.2:
          TIMELIMIT = TIMELIMIT*1.1
          sys.stdout.write("(T {0})".format(TIMELIMIT))
        else:
          FIX_RATIO = FIX_RATIO - 0.01
          sys.stdout.write("(R {0})".format(FIX_RATIO))
        FEASIBLE_COUNT = 0
        INFEASIBLE_COUNT = 0

  #g_model.setParam("TimeLimit", float('inf'))
  #g_model.optimize()
  #if g_model.status == grb.GRB.OPTIMAL:
  #  print("Optimal solution: {0}".format(g_model.objval))
  m.write(model)

if __name__ == "__main__":
  large_neighborhood(m.create_model(m.read(sys.argv[1])))
