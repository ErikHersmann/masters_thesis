from gurobi_solver import linear_solver
from pulp import PulpSolverError
import json

if __name__ == "__main__":
    with open("../../resources/config.json", "r") as f:
        config_dict = json.load(f)
    with open("../../data/output/j4s6_1.json", "r") as f:
        jobs_seminars = json.load(f)
    with open("../../data/output/machineset_2.json", "r") as f:
        machines = json.load(f)

    solver = linear_solver(machines, jobs_seminars, config_dict, True)
    solver.compile()
    try:
        solver.solve(True)
    except  PulpSolverError:
        print(f"Make sure to switch to the the right python virtual environment / pip install gurobipy")
