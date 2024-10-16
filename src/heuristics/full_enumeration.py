import itertools, json
from sys import argv


def enumerate_all_solutions(N_JOBS, N_SEMINARS, N_MACHINES):
    output = []
    idx = 0

    seminars = list(range(N_JOBS, N_JOBS + N_SEMINARS))
    job_assignments = list(itertools.product(range(N_MACHINES), repeat=N_JOBS))

    seminar_assignments = []
    for _ in seminars:
        seminar_assignments.append(
            list(
                itertools.combinations_with_replacement(
                    range(N_MACHINES + 1), N_MACHINES
                )
            )
        )

    for job_assignment in job_assignments:
        for seminar_assignment_combo in itertools.product(*seminar_assignments):
            machines = [[] for _ in range(N_MACHINES)]
            for job_idx, machine in enumerate(job_assignment):
                machines[machine].append(job_idx)
            for seminar_idx, seminar_assignment in enumerate(seminar_assignment_combo):
                for machine, count in enumerate(seminar_assignment):
                    if count > 0:
                        machines[machine].append(N_JOBS + seminar_idx)
            machine_permutations = list(
                itertools.product(*[itertools.permutations(m) for m in machines])
            )
            for perm in machine_permutations:
                solution = [list(p) for p in perm]
                output.append({"idx": idx, "solution": solution})
                idx += 1

    for solution in output:
        for m_idx in range(len(solution['solution'])):
            if (
                len(solution["solution"][m_idx]) > 0
                and solution["solution"][m_idx][-1] >= N_JOBS
            ):
                output.remove(solution)
                break

    return output


if __name__ == "__main__":
    if len(argv) >= 4:
        N_JOBS, N_SEMINARS, N_MACHINES = (int(x) for x in argv[1:5])
    else:
        N_JOBS = 5
        N_MACHINES = 2
        N_SEMINARS = 1
    result = enumerate_all_solutions(
        N_JOBS=N_JOBS, N_SEMINARS=N_SEMINARS, N_MACHINES=N_MACHINES
    )
    fname = f"results/j{N_JOBS}s{N_SEMINARS}m{N_MACHINES}_enum.json"
    with open(
        fname, "w"
    ) as f:
        json.dump(
            result,
            f,
        )
    print(f"Solution count {len(result)} ({fname})")
