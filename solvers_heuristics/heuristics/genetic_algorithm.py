import json
from calculate_lateness import calculate_lateness
from pprint import pprint
from random import randint, choice, shuffle, seed
from math import floor


# This should all work without knowledge of jobs/seminars/machines
# All that is needed is N_JOBS, N_MACHINES, N_SEMINARS
seed(7)


class genetic_algorithm:
    """Recombine Parent generation\\
    Mutate their children\\
    Repair the children\\
    Selection -> next parent generation
    """

    def __init__(self, N_JOBS, N_SEMINARS, N_MACHINES) -> None:
        with open("../../resources/config.json", "r") as f:
            self.config = json.load(f)

        self.N_JOBS = N_JOBS
        self.N_SEMINARS = N_SEMINARS
        self.N_MACHINES = N_MACHINES
        self.current_generation = []
        self.N_PARENTS = 6  # 5 is stable
        self.current_epoch = 1
        self.mutation_probability = 0.05
        self.mut_treshold = 100 - floor(100 * self.mutation_probability)
        self.lateness_calculator = None
        self.MAX_POPULATION_SIZE = 50
        self.best = [1000, None]
        self.generate_first_generation()

    def generate_first_generation(self):
        """Used to generate a semi random starting generation"""
        for _ in range(self.N_PARENTS):
            cur_solution = []
            all_jobs = list(range(self.N_JOBS + self.N_SEMINARS))
            jobs_picked = []
            for _ in range(self.N_MACHINES):
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
        self.repair()

    def mutate(self):
        """Random mutation via shuffling machine indices or job indices on a machine\\
        probability can be set via the class parameter
        """
        for candidate_index, candidate in enumerate(self.current_generation):
            if randint(1, 100) > self.mut_treshold:
                shuffle(self.current_generation[candidate_index])
            for machine_index in range(len(candidate)):
                if randint(1, 100) > self.mut_treshold:
                    shuffle(self.current_generation[candidate_index][machine_index])
        self.repair()

    def repair(self):
        """Supposed to turn all solutions into valid ones\\
        Might be buggy still
        """
        for candidate_index, candidate in enumerate(self.current_generation):
            current_jobs = []
            for machine_index in range(len(candidate)):
                current_seminars = []
                self.current_generation[candidate_index][machine_index] = list(
                    dict.fromkeys(
                        self.current_generation[candidate_index][machine_index]
                    )
                )
                for job_index, job in enumerate(
                    self.current_generation[candidate_index][machine_index]
                ):
                    if (job < self.N_JOBS and job in current_jobs) or (
                        job >= self.N_JOBS and job in current_seminars
                    ):
                        self.current_generation[candidate_index][machine_index].pop(
                            job_index
                        )
                    else:
                        current_jobs.append(job)
                        current_seminars.append(job)

            for job in range(self.N_JOBS):
                if job not in current_jobs:
                    self.current_generation[candidate_index][-1].append(job)

    def selection(self):
        """Halfs the current population count via random comparison of 2 individuals and discarding the less fit one\\
        Maybe keep the top k ones always regardless of of win or lose
        """
        while True:
            shuffle(self.current_generation)
            next_generation = []
            for idx in range(0, len(self.current_generation), 2):
                if idx == len(self.current_generation) - 1:
                    fitness2 = 10000
                else:
                    fitness2 = self.lateness_calculator.calculate(
                        self.current_generation[idx + 1]
                    )
                fitness1 = self.lateness_calculator.calculate(
                    self.current_generation[idx]
                )
                # print(fitness1, fitness2)
                if fitness1 <= fitness2:
                    next_generation.append(self.current_generation[idx])
                    if fitness1 < self.best[0]:
                        self.best = [fitness1, self.current_generation[idx]]
                else:
                    next_generation.append(self.current_generation[idx + 1])
                    if fitness2 < self.best[0]:
                        self.best = [fitness2, self.current_generation[idx]]
            self.current_generation = next_generation
            if len(self.current_generation) <= self.MAX_POPULATION_SIZE:
                break

    def recombination(self):
        """For each machine pick a random index in range 0 to minimum of the lengths of the two individuals\\
        Take all entries up to the random index from parent 1's machine and all the entries after the index from parent 2's machine
        """
        children = []
        for parent1_idx in range(len(self.current_generation)):
            for parent2_idx in range(parent1_idx + 1, len(self.current_generation)):
                children.append([])
                machine_idx = 0
                for m1, m2 in zip(
                    self.current_generation[parent1_idx],
                    self.current_generation[parent2_idx],
                ):
                    split_point = randint(0, min(len(m1), len(m2)))
                    children[-1].append(
                        self.current_generation[parent1_idx][machine_idx][
                            : split_point + 1
                        ]
                    )
                    children[-1][-1].extend(
                        self.current_generation[parent2_idx][machine_idx][split_point:]
                    )
                    machine_idx += 1
        self.current_generation = children
        self.current_epoch += 1
        self.mutate()

    def __str__(self):
        return "\n".join([str(x) for x in self.current_generation])


def setup():
    machines_path = "../../data_generation/output/machineset_0.json"
    with open(machines_path, "r") as f:
        machines = json.load(f)
    jobs_path = "../../data_generation/output/jobset_2.json"
    seminars_path = "../../data_generation/output/seminarset_basic_0.json"
    with open(jobs_path, "r") as f:
        jobs = json.load(f)
    correction_idx = len(jobs)
    with open(seminars_path, "r") as f:
        jobs.extend(json.load(f))

    for key in range(len(jobs)):
        if jobs[key]["index"] == -1:
            jobs[key]["index"] = correction_idx
            correction_idx += 1
    return (machines, jobs)


if __name__ == "__main__":
    algo = genetic_algorithm(5, 2, 3)
    algo.lateness_calculator = calculate_lateness(*setup())
    while algo.current_epoch < 20:
        algo.recombination()
        algo.selection()
    print(algo.best)
