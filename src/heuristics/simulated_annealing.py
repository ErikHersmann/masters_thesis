from algorithm_template import heuristic_template
from random import random, choices
from math import exp
from copy import deepcopy


class simulated_annealing(heuristic_template):
    """Acceptance prob function still a bit wonky """

    def __init__(self, machines, jobs_seminars) -> None:
        heuristic_template.__init__(self, machines, jobs_seminars)
        self._current_solution = None
        self._temperature = None
        self.starting_temperature = 100
        self.K_MAX = 1300
        self.k = 1
        self._best = [10000, None]
        self._visited = []
        # the higher this factor the more short solutions are favored
        self.favor_short_solutions_factor = 4
        self.generate_start()

    def generate_start(self):
        self._current_solution = [[] for _ in range(self.N_MACHINES)]
        self._current_solution[0] = list(range(self.N_JOBS))

    def temperature_generator(self, remainder):
        return self.starting_temperature * remainder

    def step(self):
        self._temperature = self.temperature_generator(1 - (self.k /self.K_MAX))
        new_neighbor = self.get_random_neighbor()
        self._visited.append(new_neighbor)
        lateness_new = self.lateness_calculator.calculate(new_neighbor)
        if lateness_new < self._best[0]:
            self._best = [lateness_new, new_neighbor]
        if self.acceptance_prob_function(new_neighbor) > random():
            self._current_solution = new_neighbor
            # print(self._current_solution, self.lateness_calculator.calculate(self._current_solution))
        self.k += 1

    def enumerate_neighbors(self):
        possible_neighbors = []
        ############################
        # INSERT OR DELETE SEMINARS#
        ############################
        for machine_idx, machine in enumerate(self._current_solution):
            current_seminars = [
                seminar
                for seminar in machine
                if seminar >= self.N_JOBS
            ]
            unassigned_seminars = [
                seminar
                for seminar in range(self.N_JOBS, self.N_JOBS + self.N_SEMINARS)
                if seminar not in current_seminars
            ]
            # Removals should be more likely
            for seminar in current_seminars:
                neighbor = deepcopy(self._current_solution)
                neighbor[machine_idx].remove(seminar)
                possible_neighbors.extend([neighbor for _ in range(self.favor_short_solutions_factor)])
            for seminar in unassigned_seminars:
                for insertion_index in range(len(self._current_solution[machine_idx])+1):
                    neighbor = deepcopy(self._current_solution)
                    neighbor[machine_idx].insert(insertion_index, seminar)
                    possible_neighbors.append(neighbor)
        ##########################
        # SWITCH JOBS OR SEMINARS#
        ##########################
        for machine_idx_1 in range(self.N_MACHINES):
            for machine_idx_2 in range(machine_idx_1, self.N_MACHINES):
                for item_1 in self._current_solution[machine_idx_1]:
                    for item_2 in self._current_solution[machine_idx_2]:
                        neighbor = deepcopy(self._current_solution)
                        if machine_idx_1 != machine_idx_2 and (item_1 in self._current_solution[machine_idx_2] or item_2 in self._current_solution[machine_idx_1]):
                            # Avoid duplicate seminars / Jobs
                            continue
                        neighbor[machine_idx_1].remove(item_1)
                        neighbor[machine_idx_1].append(item_2)
                        neighbor[machine_idx_2].remove(item_2)
                        neighbor[machine_idx_2].append(item_1)
                        possible_neighbors.append(
                            neighbor
                        )
        return [neighbor for neighbor in possible_neighbors if neighbor not in self._visited]

    def get_random_neighbor(self):
        all_neighbors = self.enumerate_neighbors()
        # Skew this towards shorter solutions
        weights = [(1/sum([len(machine) for machine in neighbor]))**self.favor_short_solutions_factor for neighbor in all_neighbors]
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        return choices(all_neighbors, normalized_weights, k=1)[0]

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
