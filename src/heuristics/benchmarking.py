import json, sys, os, time
from simulated_annealing import simulated_annealing
from genetic_algorithm import genetic_algorithm
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data.gen_jobs_and_seminars import generate_jobs_seminars
from data.gen_ran_machines import generate_machines
from calculate_lateness import calculate_lateness
from solvers.gurobi_solver import linear_solver


if __name__ == "__main__":
    if len(sys.argv) == 4:
        N_JOBS, N_SEMINARS, N_MACHINES = map(int, sys.argv[1:])
    else:
        # Set N_SEMINARS to None if u want 6
        N_JOBS, N_SEMINARS, N_MACHINES = 4, 2, 2
    small_instance = all([N_SEMINARS <= 2, N_JOBS <= 5, N_MACHINES <= 3])
    # small_instance = False
    ########
    # SETUP#
    ########
    with open("../../resources/config.json", "r") as f:
        config_dict = json.load(f)
    machines = generate_machines(N_MACHINES, config_dict)
    jobs = generate_jobs_seminars(N_JOBS, config_dict, N_SEMINARS)
    N_JOBS = sum([1 for job in jobs if job["type"] == "job"])
    N_SEMINARS = sum([1 for job in jobs if job["type"] == "seminar"])
    setup_tuple = (machines, jobs)
    lateness_calculator = calculate_lateness(machines, jobs, config_dict, True, True)
    print(f"N_JOBS {N_JOBS} N_SEMINARS {N_SEMINARS} N_MACHINES {N_MACHINES}")

    ####################
    # GENETIC ALGORITHM#
    ####################
    print(f"Genetic algorithm")
    start = time.time_ns()
    algo1 = genetic_algorithm(*setup_tuple, config_dict)
    while algo1._current_epoch < algo1.MAX_EPOCH:
        algo1.recombination()
        algo1.selection()
    finish_1 = (time.time_ns() - start) / 10**9
    print([algo1._best[0], algo1._best[1][0], len(algo1._best[1])])
    lateness_calculator.calculate(algo1._best[1][0])

    ######################
    # SIMULATED ANNEALING#
    ######################
    print(f"Simulated annealing")
    start = time.time_ns()
    algo2 = simulated_annealing(*setup_tuple, config_dict)
    while algo2.k < algo2.K_MAX:
        algo2.step()
    finish_2 = (time.time_ns() - start) / 10**9
    print([algo2._best[0], algo2._best[1][0], len(algo2._best[1])])
    lateness_calculator.calculate(algo2._best[1][0])

    ###################
    # HYBRID ALGORITHM#
    ###################
    print(f"Hybrid algorithm")
    start = time.time_ns()
    algo5 = simulated_annealing(*setup_tuple, config_dict)
    algo5._current_solution = algo1._best[1][0] 
    algo5._best = [algo1._best[0], [algo1._best[1][0]]]
    while algo5.k < algo5.K_MAX:
        algo5.step()
    finish_5 = (time.time_ns() - start) / 10**9
    print([algo5._best[0], algo5._best[1][0], len(algo5._best[1])])
    lateness_calculator.calculate(algo5._best[1][0])

    ###################
    # FULL ENUMERATION#
    ###################
    solutions_path = f"results/j{N_JOBS}s{N_SEMINARS}m{N_MACHINES}_enum.json"
    if os.path.isfile(solutions_path):
        print(f"Full enumeration")
        start = time.time_ns()
        with open(solutions_path, "r") as f:
            solutions = json.load(f)
        calculator = calculate_lateness(machines, jobs, config_dict)
        algo3_best = [1000, []]
        for row_idx, solution in enumerate(solutions):
            lateness = calculator.calculate(solution["solution"])
            solutions[row_idx]["lateness"] = lateness
            if lateness < algo3_best[0]:
                algo3_best = [lateness, [solution]]
            elif lateness == algo3_best[0]:
                algo3_best[1].append(solution)
        finish_3 = (time.time_ns() - start) / 10**9
        print([algo3_best[0], algo3_best[1][0]['solution'], len(algo3_best[1])])
        lateness_calculator.calculate(algo3_best[1][0]['solution'])
        with open(solutions_path, "w") as f:
            json.dump(solutions, f)
        opt_solution_count = len(algo3_best[1])
    else:
        print(f"No enumeration file found")
        algo3_best = [None, None]
        finish_3 = None
        solutions = []
        opt_solution_count = None

    #########
    # GUROBI#
    #########
    if small_instance:
        start = time.time_ns()
        solver = linear_solver(
            machines,
            jobs,
            config_dict,
            verbose=False,
        )
        solver.compile()
        gurobi_lateness, gurobi_solution = solver.solve(write_verbose_output=True, terminal_output=True)
        print(f"Gurobi\n{[int(gurobi_lateness), gurobi_solution]}")
        lateness_calculator.calculate(gurobi_solution)
        finish_4 = (time.time_ns() - start) / 10**9
        gurobi_calculated_lateness = calculator.calculate(gurobi_solution)
    else:
        print(f"Model size too large for MIP solver")
        gurobi_lateness = None
        gurobi_calculated_lateness = None
        gurobi_solution = None
        finish_4 = None

    ################
    # WRITE RESULTS#
    ################
    epoch_time = int(time.time())
    results = {
        "solutions": {
            "genetic_algorithm": {
                "lateness": algo1._best[0],
                "solution": algo1._best[1],
                "runtime_seconds": finish_1,
                "max_epoch": algo1.MAX_EPOCH,
            },
            "simulated_annealing": {
                "lateness": algo2._best[0],
                "solution": algo2._best[1],
                "runtime_seconds": finish_2,
                "max_k": algo2.K_MAX,
            },
            "full_enumeration": {
                "lateness": algo3_best[0],
                "optimal_solutions": algo3_best[1],
                "runtime_seconds": finish_3,
                "solution_count": len(solutions),
                "optimal_solution_count": opt_solution_count,
            },
            "gurobi": {
                "lateness_model": gurobi_lateness,
                "lateness" : gurobi_calculated_lateness,
                "solution": gurobi_solution,
                "runtime_seconds": finish_4,
            },
        },
        "machines": machines,
        "jobs_seminars": jobs,
    }
    with open(f"results/benchmark/{epoch_time}_benchmark.json", "w") as f:
        json.dump(results, f)
    print(f"Saved as {epoch_time}_benchmark.json")
