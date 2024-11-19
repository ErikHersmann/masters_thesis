import itertools, json
from sys import argv


def generate_reorderings(list_of_lists):
    # Generate permutations for each inner list
    permuted_inner_lists = [list(itertools.permutations(inner)) for inner in list_of_lists]

    # Compute all combinations of these permutations
    all_combinations = list(itertools.product(*permuted_inner_lists))
    return [list(map(list, combination)) for combination in all_combinations]


def generate_all_insertions(list1, list2):
    """
    Generate all possible ways to insert elements of list2 into list1,
    preserving the order of elements in list2.

    Args:
    - list1: The first list possibly empty
    - list2: The second list also possibly empty

    Returns:
    - A list of all possible insertions (A list of all valid insertions on 1 machine)
    """
    if not list2:
        return [list1]

    results = []
    # Find all positions in list1 where items of list2 can be inserted
    for positions in itertools.combinations(range(len(list1) + len(list2)), len(list2)):
        new_list = list1[:]  # Make a copy of list1 to insert into
        for idx, pos in enumerate(positions):
            new_list.insert(
                pos, list2[idx]
            )  # Insert each element of list2 in the specified position
        results.append(new_list)

    return results


def enumerate_all_solutions(N_JOBS, N_SEMINARS, N_MACHINES):
    output = []
    idx = 0

    seminars = list(range(N_JOBS, N_JOBS + N_SEMINARS))
    # All possible assignments to assign all jobs to all machines in all orders
    # (This contains a list of length N_MACHINES with each value corresponding
    # to a machine index on which the current index (JOB) should be put)
    job_assignments = list(itertools.product(range(N_MACHINES), repeat=N_JOBS))

    # Generate all possible sublists for each machine (including empty lists)
    seminar_assignments = [
        list(itertools.permutations(seminars, r)) for r in range(len(seminars) + 1)
    ]
    # Flatten to get all possible sublists for a single machine
    seminar_assignments = [list(p) for sublist in seminar_assignments for p in sublist]

    # Create product of all machines with these sublists
    seminar_assignments = itertools.product(seminar_assignments, repeat=N_MACHINES)
    seminar_assignments = [
        list(map(list, machine_combination))
        for machine_combination in seminar_assignments
    ]

    for job_assignment in job_assignments:
        # Set up the job order
        unordered_machines = [[] for _ in range(N_MACHINES)]
        for job_idx, machine_idx in enumerate(job_assignment):
            unordered_machines[machine_idx].append(job_idx)

        # All combinations of these machine assignments (orders)
        for machines in generate_reorderings(unordered_machines):
            # Add the seminars
            for seminar_assignment in seminar_assignments:
                possible_machine_assignments = [
                    generate_all_insertions(
                        machines[machine_idx], seminar_assignments_on_machine
                    )
                    for machine_idx, seminar_assignments_on_machine in enumerate(
                        seminar_assignment
                    )
                ]
                # calculate all recombinations of machines of all the current producable seminar insertion
                for combination in itertools.product(*possible_machine_assignments):
                    current_solution = list(combination)
                    # Filtering out "trailing seminar" solutions (since these will always be weakly dominated by their equivalent with the trailing seminar stripped)
                    if all(
                        [
                            False if len(machine) > 0 and machine[-1] >= N_JOBS else True
                            for machine in current_solution
                        ]
                    ):
                        output.append({"idx": idx, "solution": current_solution})
                        idx += 1
    return output


if __name__ == "__main__":
    if len(argv) >= 4:
        N_JOBS, N_SEMINARS, N_MACHINES = (int(x) for x in argv[1:5])
    else:
        print("Exiting with code -1")
        exit(-1)
    result = enumerate_all_solutions(
        N_JOBS=N_JOBS, N_SEMINARS=N_SEMINARS, N_MACHINES=N_MACHINES
    )
    fname = f"results/j{N_JOBS}s{N_SEMINARS}m{N_MACHINES}_enum_v2.json"
    with open(fname, "w") as f:
        json.dump(
            result,
            f,
        )
    print(f"Solution count {len(result)} ({fname})")
