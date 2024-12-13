from algorithm_template import heuristic_template
from random import random, choice, shuffle, randint, choices
from math import exp
from copy import deepcopy


class simulated_annealing(heuristic_template):
    """Acceptance prob function still a bit wonky"""

    def __init__(self, machines, jobs_seminars, config_dict, T=100, max_epoch=10000, favor_short_solutions_factor=1) -> None:
        heuristic_template.__init__(self, machines, jobs_seminars, config_dict)
        self._current_solution = None
        self._temperature = None
        self.starting_temperature = T
        self.K_MAX = max_epoch
        self.k = 1
        self._best = [10000, None]
        self._visited = []
        # the higher this factor the more short solutions are favored
        self.favor_short_solutions_factor = favor_short_solutions_factor
        self.generate_start()

    def generate_start(self):
        possible_jobs = list(range(self.N_JOBS))
        shuffle(possible_jobs)
        self._current_solution = [[] for _ in range(self.N_MACHINES)]
        for job in possible_jobs:
            self._current_solution[randint(0, len(self._current_solution) - 1)].append(
                job
            )

    def update_temperature(self, mode=0):
        if mode == 0:
            # This is the one that produces better results ?
            self._temperature = self.starting_temperature * (0.99**self.k)
        elif mode == 1:
            remainder = 1 - (self.k / self.K_MAX)
            self._temperature = self.starting_temperature * remainder

    def step(self):
        self.update_temperature()
        new_neighbor = self.get_random_neighbor()
        self._visited.append(new_neighbor)
        lateness_new = self.lateness_calculator.calculate(new_neighbor)
        if lateness_new < self._best[0]:
            self._best = [lateness_new, [new_neighbor]]
        elif lateness_new == self._best[0] and new_neighbor not in self._best[1]:
            self._best[1].append(new_neighbor)
        if self.acceptance_prob_function(new_neighbor) > random():
            self._current_solution = new_neighbor
        self.k += 1

    def get_some_semi_random_neighbors(self):
        possible_neighbors = []
        ############################
        # INSERT OR DELETE SEMINARS#
        ############################
        machine_idx = choices(
            list(range(self.N_MACHINES)),
            weights=[len(machine) for machine in self._current_solution],
            k=1,
        )[0]
        machine = self._current_solution[machine_idx]
        current_seminars = [seminar for seminar in machine if seminar >= self.N_JOBS]
        unassigned_seminars = [
            seminar
            for seminar in range(self.N_JOBS, self.N_JOBS + self.N_SEMINARS)
            if seminar not in current_seminars
        ]
        shuffle(unassigned_seminars)
        # Removals should be more likely
        for seminar in current_seminars:
            neighbor = deepcopy(self._current_solution)
            neighbor[machine_idx].remove(seminar)
            possible_neighbors.extend(
                [neighbor for _ in range(self.favor_short_solutions_factor)]
            )
        removed_seminar_count = (
            len(current_seminars) if len(current_seminars) > 0 else 2
        )
        added_seminar_count = 0
        for seminar in unassigned_seminars:
            if added_seminar_count == removed_seminar_count:
                break
            insertion_index = choice(
                list(range(len(self._current_solution[machine_idx]) + 1))
            )
            neighbor = deepcopy(self._current_solution)
            neighbor[machine_idx].insert(insertion_index, seminar)
            possible_neighbors.append(neighbor)
            added_seminar_count += 1
        ###########
        # SWAPPING#
        ###########
        machine_idx_1 = choice(list(range(self.N_MACHINES)))
        indices_free_to_choose = list(range(self.N_MACHINES))
        indices_free_to_choose.remove(machine_idx_1)
        machine_idx_2 = choice(indices_free_to_choose)
        for item_1 in [
            x for x in self._current_solution[machine_idx_1] if x < self.N_JOBS
        ]:
            for item_2 in [
                x for x in self._current_solution[machine_idx_2] if x < self.N_JOBS
            ]:
                neighbor = deepcopy(self._current_solution)
                if (
                    item_1 in self._current_solution[machine_idx_2]
                    or item_2 in self._current_solution[machine_idx_1]
                ):
                    continue
                ###########
                # SWAPPING#
                ###########
                neighbor[machine_idx_1].remove(item_1)
                neighbor[machine_idx_1].append(item_2)
                neighbor[machine_idx_2].remove(item_2)
                neighbor[machine_idx_2].append(item_1)
                # if neighbor not in self._visited:
                possible_neighbors.append(neighbor)
                #     self._visited.append(neighbor)

        ret_val = possible_neighbors
        while len(ret_val) == 0:
            ret_val = self.get_some_semi_random_neighbors()
        return ret_val

    def get_random_neighbor(self):
        return choice(self.get_some_semi_random_neighbors())

    def acceptance_prob_function(self, new):
        # old, new, temp
        old_obj = self.lateness_calculator.calculate(self._current_solution)
        new_obj = self.lateness_calculator.calculate(new)
        if old_obj > new_obj:
            return 1.0
        try:
            return exp((-(new_obj - old_obj)) / self._temperature)
        except OverflowError:
            return 0.0

    def run(self):
        while self.k < self.K_MAX:
            self.step()