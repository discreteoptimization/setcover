"""Large neighborhood search for set cover based on an MIP solver.

My approach is to improve the solution by keeping a fixed ratio of
the variables constant"""

import random
import sys
import gurobipy as grb
import mip as m

# Time limit per MIP call in s
TIMELIMIT = 1.0 * 60
# Ratio of unused nodes to fix
FIX_RATIO = 0.5


def large_neighborhood(model):
  """Solves a set cover instance with large-neighborhood
  search.

  In each call to the MIP solver we exclude a fixed ratio of the sets that
  are currently unused. (Is this sensible? Should I favor excluding
  more costly sets?)
  """
  g_model, vars = model

  # Do not pollute stdout
  g_model.setParam("OutputFlag", 0)

  print("Processing " + g_model.getAttr("ModelName"))

  # Warmup
  m.solve(model, TIMELIMIT)
  print("Initial solution: {0}".format(g_model.objval))
  m.write(model)

  if g_model.status != grb.GRB.OPTIMAL:
    while g_model.status != grb.GRB.INTERRUPTED:
      # Add new constraints as described above
      added_constraints = []
      for var in vars:
        if int(var.x) == 0 and random.random() < FIX_RATIO:
          added_constraints.append(g_model.addConstr(var == 0))

      # Next iteration
      m.solve(model, TIMELIMIT, False)

      # Remove old constraints
      for constraint in added_constraints:
        g_model.remove(constraint)

      print("Next solution:    {0}".format(g_model.objval))
      m.write(model, False)

  m.solve(model, TIMELIMIT, False)
  print("Optimal solution: {0}".format(g_model.objval))
  m.write(model)

if __name__ == "__main__":
  large_neighborhood(m.create_model(m.read(sys.argv[1])))
