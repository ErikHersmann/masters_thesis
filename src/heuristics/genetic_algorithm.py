import json
from random import randint, choice, shuffle, seed
from math import floor
from algorithm_template import heuristic_template


# This should all work without knowledge of jobs/seminars/machines
# All that is needed is N_JOBS, N_MACHINES, N_SEMINARS
seed(7)


class genetic_algorithm(heuristic_template):
    """Recombine Parent generation\\
    Mutate their children\\
    Repair the children\\
    Selection -> next parent generation
    """

    def __init__(self, machines, jobs_seminars) -> None:
        heuristic_template.__init__(self, machines, jobs_seminars)
        self.N_PARENTS = 6  # 5 is naturally repeating (5 parents generate 10 children, which become 5 parents after 1 round of selection)
        self.MAX_POP_SIZE = 50
        self.F_MUT_PROB = 0.05
        self._current_epoch = 1
        self._mut_treshold = 100 - floor(100 * self.F_MUT_PROB)
        self._best = [1000, None]
        self._current_generation = []
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
            self._current_generation.append(cur_solution)
        self.repair()

    def mutate(self):
        """Random mutation via shuffling machine indices or job indices on a machine\\
        probability can be set via the class parameter
        """
        for candidate_index, candidate in enumerate(self._current_generation):
            if randint(1, 100) > self._mut_treshold:
                shuffle(self._current_generation[candidate_index])
            for machine_index in range(len(candidate)):
                if randint(1, 100) > self._mut_treshold:
                    shuffle(self._current_generation[candidate_index][machine_index])
        self.repair()

    def repair(self):
        """Supposed to turn all solutions into valid ones\\
        Might be buggy still
        """
        for candidate_index, candidate in enumerate(self._current_generation):
            current_jobs = []
            for machine_index in range(len(candidate)):
                current_seminars = []
                self._current_generation[candidate_index][machine_index] = list(
                    dict.fromkeys(
                        self._current_generation[candidate_index][machine_index]
                    )
                )
                for job_index, job in enumerate(
                    self._current_generation[candidate_index][machine_index]
                ):
                    if (job < self.N_JOBS and job in current_jobs) or (
                        job >= self.N_JOBS and job in current_seminars
                    ):
                        self._current_generation[candidate_index][machine_index].pop(
                            job_index
                        )
                    else:
                        current_jobs.append(job)
                        current_seminars.append(job)

            for job in range(self.N_JOBS):
                if job not in current_jobs:
                    self._current_generation[candidate_index][-1].append(job)

    def selection(self):
        """Halfs the current population count via random comparison of 2 individuals and discarding the less fit one\\
        Maybe keep the top k ones always regardless of of win or lose
        """
        while True:
            shuffle(self._current_generation)
            next_generation = []
            for idx in range(0, len(self._current_generation), 2):
                if idx == len(self._current_generation) - 1:
                    fitness2 = 10000
                else:
                    fitness2 = self.lateness_calculator.calculate(
                        self._current_generation[idx + 1]
                    )
                fitness1 = self.lateness_calculator.calculate(
                    self._current_generation[idx]
                )
                # print(fitness1, fitness2)
                if fitness1 <= fitness2:
                    next_generation.append(self._current_generation[idx])
                    if fitness1 < self._best[0]:
                        self._best = [fitness1, self._current_generation[idx]]
                else:
                    next_generation.append(self._current_generation[idx + 1])
                    if fitness2 < self._best[0]:
                        self._best = [fitness2, self._current_generation[idx]]
            self._current_generation = next_generation
            if len(self._current_generation) <= self.MAX_POP_SIZE:
                break

    def recombination(self):
        """For each machine pick a random index in range 0 to minimum of the lengths of the two individuals\\
        Take all entries up to the random index from parent 1's machine and all the entries after the index from parent 2's machine
        """
        children = []
        for parent1_idx in range(len(self._current_generation)):
            for parent2_idx in range(parent1_idx + 1, len(self._current_generation)):
                children.append([])
                machine_idx = 0
                for m1, m2 in zip(
                    self._current_generation[parent1_idx],
                    self._current_generation[parent2_idx],
                ):
                    split_point = randint(0, min(len(m1), len(m2)))
                    children[-1].append(
                        self._current_generation[parent1_idx][machine_idx][
                            : split_point + 1
                        ]
                    )
                    children[-1][-1].extend(
                        self._current_generation[parent2_idx][machine_idx][split_point:]
                    )
                    machine_idx += 1
        self._current_generation = children
        self._current_epoch += 1
        self.mutate()

    def __str__(self):
        return "\n".join([str(x) for x in self._current_generation])


def setup():
    machines_path = "../../data/output/machineset_0.json"
    with open(machines_path, "r") as f:
        machines = json.load(f)
    jobs_path = "../../data/output/jobset_2.json"
    seminars_path = "../../data/output/seminarset_basic_0.json"
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
    algo = genetic_algorithm(*setup())
    while algo._current_epoch < 20:
        algo.recombination()
        algo.selection()
    print(algo._best)
