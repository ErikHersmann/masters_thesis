import itertools, json


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

    return output


if __name__ == "__main__":
    N_JOBS = 2
    N_MACHINES = 2
    N_SEMINARS = 3
    with open(
        f"results/jobs-{N_JOBS}_seminars-{N_SEMINARS}_machines-{N_MACHINES}.json", "w"
    ) as f:
        json.dump(
            enumerate_all_solutions(
                N_JOBS=N_JOBS, N_SEMINARS=N_SEMINARS, N_MACHINES=N_MACHINES
            ),
            f,
        )
