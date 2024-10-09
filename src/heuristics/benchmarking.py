import json, sys, os
from simulated_annealing import simulated_annealing
from genetic_algorithm import genetic_algorithm
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from data.gen_jobs_and_seminars import generate_jobs_seminars
from data.gen_ran_machines import generate_machines


def setup():
    with open("../../data/output/machineset_0.json", "r") as f:
        machines = json.load(f)
    with open("../../data/output/jobset_4.json", "r") as f:
        jobs = json.load(f)
    return (machines, jobs)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        N_MACHINES, N_JOBS = map(int, sys.argv[1:])
    else:
        N_MACHINES, N_JOBS = 5, 3
    machines = generate_machines(N_MACHINES)
    jobs = generate_jobs_seminars(N_JOBS)
    N_JOBS = sum([1 for job in jobs if job["type"] == "job"])
    N_SEMINARS = sum([1 for job in jobs if job["type"] == "seminar"])
    # setup_tuple = setup()
    setup_tuple = (machines, jobs)
    print(
            f"N_MACHINES {N_MACHINES} N_JOBS {N_JOBS} N_SEMINARS {N_SEMINARS}"
        )
    print(f"Genetic algorithm")
    algo = genetic_algorithm(*setup_tuple)
    while algo._current_epoch < algo.MAX_EPOCH:
        algo.recombination()
        algo.selection()
    print(algo._best)

    print(f"Simulated annealing")
    algo = simulated_annealing(*setup_tuple)
    while algo.k < algo.K_MAX:
        algo.step()
    print(algo._best)
