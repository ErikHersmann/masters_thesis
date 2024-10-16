from gurobi_solver import linear_solver
from pulp import PulpSolverError
import json

if __name__ == "__main__":
    with open("../../resources/config.json", "r") as f:
        config_dict = json.load(f)
    # with open("../../data/output/j5s1_0.json", "r") as f:
    # jobs_seminars = json.load(f)
    # with open("../../data/output/m2_0.json", "r") as f:
    # machines = json.load(f)
    with open(
        "../heuristics/results/1729047986_benchmark.json",
        "r",
    ) as f:
        benchmarking_reference = json.load(f)

    # solver = linear_solver(machines, jobs_seminars, config_dict, True)
    solver = linear_solver(benchmarking_reference['machines'], benchmarking_reference['jobs_seminars'], config_dict, True)
    solver.compile()
    try:
        solver.solve(True)
    except  PulpSolverError:
        print(f"Make sure to switch to the the right python virtual environment / pip install gurobipy")
