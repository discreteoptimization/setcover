#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Large neighborhood search for set cover based on a MIP solver.

The approach is to improve the solution by fixing a ratio of the currently
unused nodes. I took the idea from https://github.com/ricbit/setcover.
On my computer this yields solutions that suffice for getting a 10
in under 15 minutes.
"""

import random
import sys
import gurobipy as grb
import mip as m

# Time limit per MIP call in s
TIMELIMIT = 2.5 * 60
# Ratio of unused nodes to exclude
FIX_RATIO = 0.6


def large_neighborhood(model):
  """
  Solves a set cover instance with large-neighborhood search.

  In each call to the MIP solver we exclude a fixed ratio of the sets that
  are currently unused. (Maybe I should favor excluding
  the sets with the highest cost/size ratio?)

  Args:
    model: The set cover MIP model as created by mip.create_model().
  """
  g_model, vars = model
  g_model.setParam("OutputFlag", 0)
  g_model.setParam("TimeLimit", TIMELIMIT)
  g_model.setParam("SolutionLimit", 1)

  print("Processing " + g_model.getAttr("ModelName"))

  # Warmup
  g_model.optimize()
  print("Initial solution: {0}".format(g_model.objval))
  m.write(model)
  g_model.setParam("SolutionLimit", 2147483647)
  
  best_obj = g_model.objval
  best_sol = {var:int(var.x) for var in vars}
  obj_constraint = g_model.addConstr(g_model.getObjective() <= best_obj - 1)
  
  if g_model.status != grb.GRB.OPTIMAL:
    while g_model.status != grb.GRB.INTERRUPTED:
      # Add the additional constraints as described above
      added_constraints = []
      for var in vars:
        if best_sol[var] == 0 and random.random() < FIX_RATIO:
          added_constraints.append(g_model.addConstr(var == 0))

      g_model.optimize()

      # Remove the additional constraints again
      for constraint in added_constraints:
        g_model.remove(constraint)

      #print g_model.status
      if g_model.status != grb.GRB.INFEASIBLE:
        if g_model.objval < best_obj:
          print("\nNext solution:    {0}".format(g_model.objval))
          m.write(model, False)

          best_obj = g_model.objval
          best_sol = {var:int(var.x) for var in vars}

          g_model.remove(obj_constraint)
          obj_constraint = g_model.addConstr(g_model.getObjective() <= best_obj - 1)
        else:
          print "(ERROR)"
      else:
        sys.stdout.write('.')
        sys.stdout.flush()


  g_model.setParam("TimeLimit", float('inf'))
  g_model.optimize()
  if g_model.status == grb.GRB.OPTIMAL:
    print("Optimal solution: {0}".format(g_model.objval))
  m.write(model)

if __name__ == "__main__":
  large_neighborhood(m.create_model(m.read(sys.argv[1])))
