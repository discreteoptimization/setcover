"""
Large neighborhood search for set cover based on a MIP solver.

The approach is to improve the solution by fixing some ratio of the currently
taken nodes. I took the idea from https://github.com/ricbit/setcover.
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

  print("Processing " + g_model.getAttr("ModelName"))

  # Warmup
  g_model.optimize()
  print("Initial solution: {0}".format(g_model.objval))
  m.write(model)

  if g_model.status != grb.GRB.OPTIMAL:
    while g_model.status != grb.GRB.INTERRUPTED:
      # Add the additional constraints as described above
      added_constraints = []
      for var in vars:
        if int(var.x) == 0 and random.random() < FIX_RATIO:
          added_constraints.append(g_model.addConstr(var == 0))

      # Next iteration
      g_model.optimize()

      # Remove the additional constraints again
      for constraint in added_constraints:
        g_model.remove(constraint)

      print("Next solution:    {0}".format(g_model.objval))
      m.write(model, False)

  g_model.setParam("TimeLimit", float('inf'))
  g_model.optimize()
  if g_model.status == grb.GRB.OPTIMAL:
    print("Optimal solution: {0}".format(g_model.objval))
  m.write(model)

if __name__ == "__main__":
  large_neighborhood(m.create_model(m.read(sys.argv[1])))
