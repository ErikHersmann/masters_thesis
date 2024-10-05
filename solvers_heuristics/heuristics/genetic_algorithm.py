import json
from calculate_lateness import calculate_lateness_directly
from pprint import pprint
from random import randint, choice, shuffle
from math import floor


# This should all work without knowledge of jobs/seminars/machines
# All that is needed is N_JOBS, N_MACHINES, N_SEMINARS


class genetic_algorithm:
    def __init__(self, N_JOBS, N_SEMINARS, N_MACHINES) -> None:
        with open("../../resources/config.json", "r") as f:
            self.config = json.load(f)

        self.N_JOBS = N_JOBS
        self.N_SEMINARS = N_SEMINARS
        self.N_MACHINES = N_MACHINES
        self.current_generation = []
        self.N_FIRST_GEN = 4
        self.current_epoch = 1
        self.mutation_probability = 0.05

    def generate_first_generation(self):
        print(f"j{self.N_JOBS} s{self.N_SEMINARS} m{self.N_MACHINES}")
        for _ in range(self.N_FIRST_GEN):
            cur_solution = []
            all_jobs = list(range(self.N_JOBS + self.N_SEMINARS))
            jobs_picked = []
            for machine_idx in range(self.N_MACHINES):
                cur_solution.append([])
                while randint(0, 1) == 1 and len(jobs_picked) < self.N_JOBS - 1:
                    idx = choice(all_jobs)
                    while idx in jobs_picked or idx in cur_solution[-1]:
                        idx = choice(all_jobs)
                    if idx < self.N_JOBS - 1:
                        jobs_picked.append(idx)
                    cur_solution[-1].append(idx)
            # If jobs remain here
            if len(jobs_picked) < self.N_JOBS - 1:
                for job_index in range(self.N_JOBS):
                    if all_jobs[job_index] not in jobs_picked:
                        cur_solution[-1].append(all_jobs[job_index])
            self.current_generation.append(cur_solution)

    def mutate(self):
        # print(f"Mutating")
        for candidate_index, candidate in enumerate(self.current_generation):
            for machine_index in range(len(candidate)):
                if randint(1, 100) > (100 - floor(100 * self.mutation_probability)):
                    shuffle(self.current_generation[candidate_index][machine_index])
                    # print(f"Shuffled {candidate_index} {machine_index}")

    def repair(self):
        # Not all jobs are there
        # Jobs, Seminars are double
        for candidate_index, candidate in enumerate(self.current_generation):
            current_jobs = []
            for machine_index in range(len(candidate)):
                self.current_generation[candidate_index][machine_index] = list(
                    set(self.current_generation[candidate_index][machine_index])
                )
                for job_index, job in self.current_generation[candidate_index][
                    machine_index
                ]:
                    if job < self.N_JOBS and job in current_jobs:
                        self.current_generation[candidate_index][machine_index].pop(
                            job_index
                        )
                current_jobs.extend(
                    self.current_generation[candidate_index][machine_index]
                )
            for job in range(self.N_JOBS):
                if job not in current_jobs:
                    self.current_generation[candidate_index][-1].append(job)

    def selection(self):
        pass

    def recombination(self):
        pass

    def __str__(self):
        return "\n".join([str(x) for x in self.current_generation])


if __name__ == "__main__":
    algo = genetic_algorithm(3, 2, 2)
    algo.generate_first_generation()
    print(algo)
    algo.mutate()
    print(algo)
    # add lateness to each individual
    # recombine them
    # mutate them
    # repair them
    # selection
