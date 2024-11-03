from random import randint, choice, shuffle, seed
from math import floor
from algorithm_template import heuristic_template


class genetic_algorithm(heuristic_template):
    """Recombine Parent generation\\
    Mutate their children\\
    Repair the children\\
    Selection -> next parent generation
    """

    def __init__(self, machines, jobs_seminars, config_dict) -> None:
        heuristic_template.__init__(self, machines, jobs_seminars, config_dict)
        seed(7)
        self.N_PARENTS = 6
        self.MAX_EPOCH = 4000
        self.F_MUT_PROB = 0.10
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
        """Selects the top N_PARENTS individuals and updates global bests
        """
        next_generation = []
        for idx in range(len(self._current_generation)):
            fitness = self.lateness_calculator.calculate(
                self._current_generation[idx]
            )
            if self._current_generation[idx] not in [child[1] for child in next_generation]:
               next_generation.append((fitness, self._current_generation[idx]))
        next_generation.sort(key=lambda x: x[0])
        self._current_generation = [child[1] for child in next_generation[:self.N_PARENTS]]
        for fitness, child in next_generation:
            if fitness < self._best[0]:
                self._best = [fitness, [child]]
            elif fitness == self._best[0]:
                self._best[1].append(child)

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



