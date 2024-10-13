import json, sys, os, time
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
    with open("../../resources/config.json", "r") as f:
        config_dict = json.load(f)
    machines = generate_machines(N_MACHINES, config_dict)
    jobs = generate_jobs_seminars(N_JOBS, config_dict)
    N_JOBS = sum([1 for job in jobs if job["type"] == "job"])
    N_SEMINARS = sum([1 for job in jobs if job["type"] == "seminar"])
    # setup_tuple = setup()
    setup_tuple = (machines, jobs)
    print(f"N_MACHINES {N_MACHINES} N_JOBS {N_JOBS} N_SEMINARS {N_SEMINARS}")
    print(f"Genetic algorithm")
    start = time.time_ns()
    algo = genetic_algorithm(*setup_tuple, config_dict)
    while algo._current_epoch < algo.MAX_EPOCH:
        algo.recombination()
        algo.selection()
    finish_1 = (time.time_ns() - start) / 10**9
    print(algo._best)

    print(f"Simulated annealing")
    start = time.time_ns()
    algo2 = simulated_annealing(*setup_tuple, config_dict)
    while algo2.k < algo2.K_MAX:
        algo2.step()
    finish_2 = (time.time_ns() - start) / 10**9
    print(algo2._best)

    epoch_time = int(time.time())
    results = {
        "solutions": {
            "genetic_algorithm": {
                "lateness": algo._best[0],
                "solution": algo._best[1],
                "runtime_seconds": finish_1,
                "max_epoch": algo.MAX_EPOCH,
            },
            "simulated_annealing": {
                "lateness": algo2._best[0],
                "solution": algo2._best[1],
                "runtime_seconds": finish_2,
                "max_k": algo2.K_MAX,
            },
        },
        "machines": machines,
        "jobs_seminars": jobs,
    }
    with open(f"results/{epoch_time}_benchmark.json", "w") as f:
        json.dump(results, f)
    print(f"results at {epoch_time}_benchmark.json")
