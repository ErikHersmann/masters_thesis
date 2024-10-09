from algorithm_template import heuristic_template
from random import choice, random
from math import e, exp
import json
from copy import deepcopy


class simulated_annealing(heuristic_template):
    """Acceptance prob function still a bit wonky """

    def __init__(self, machines, jobs_seminars) -> None:
        heuristic_template.__init__(self, machines, jobs_seminars)
        self.current_solution = None
        self.temperature = None
        self._starting_temperature = 100
        self.K_MAX = 2000
        self.k = 1
        self.best = [10000, None]
        self.visited = []
        self.generate_start()

    def generate_start(self):
        self.current_solution = [[] for _ in range(self.N_MACHINES)]
        self.current_solution[0] = list(range(self.N_JOBS))
        
    def temperature_generator(self, remainder):
        return self._starting_temperature * remainder

    def step(self):
        self.temperature = self.temperature_generator(1 - (self.k /self.K_MAX))
        new_neighbor = self.get_random_neighbor()
        self.visited.append(new_neighbor)
        lateness_new = self.lateness_calculator.calculate(new_neighbor)
        if lateness_new < self.best[0]:
            self.best = [lateness_new, new_neighbor]
        if self.acceptance_prob_function(new_neighbor) > random():
            self.current_solution = new_neighbor
            print(self.current_solution, self.lateness_calculator.calculate(self.current_solution))
        self.k += 1

    def enumerate_neighbors(self):
        possible_neighbors = []
        ############################
        # INSERT OR DELETE SEMINARS#
        ############################
        for machine_idx, machine in enumerate(self.current_solution):
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
            for seminar in current_seminars:
                neighbor = deepcopy(self.current_solution)
                neighbor[machine_idx].remove(seminar)
                possible_neighbors.append(neighbor)
            for seminar in unassigned_seminars:
                for insertion_index in range(len(self.current_solution[machine_idx])+1):
                    neighbor = deepcopy(self.current_solution)
                    neighbor[machine_idx].insert(insertion_index, seminar)
                    possible_neighbors.append(neighbor)
        ##########################
        # SWITCH JOBS OR SEMINARS#
        ##########################
        for machine_idx_1 in range(self.N_MACHINES):
            for machine_idx_2 in range(machine_idx_1, self.N_MACHINES):
                for item_1 in self.current_solution[machine_idx_1]:
                    for item_2 in self.current_solution[machine_idx_2]:
                        neighbor = deepcopy(self.current_solution)
                        if machine_idx_1 != machine_idx_2 and (item_1 in self.current_solution[machine_idx_2] or item_2 in self.current_solution[machine_idx_1]):
                            # Avoid duplicate seminars / Jobs
                            continue
                        neighbor[machine_idx_1].remove(item_1)
                        neighbor[machine_idx_1].append(item_2)
                        neighbor[machine_idx_2].remove(item_2)
                        neighbor[machine_idx_2].append(item_1)
                        possible_neighbors.append(
                            neighbor
                        )
        return [neighbor for neighbor in possible_neighbors if neighbor not in self.visited]

    def get_random_neighbor(self):
        return choice(self.enumerate_neighbors())

    def acceptance_prob_function(self, new):
        # old, new, temp
        old_obj = self.lateness_calculator.calculate(self.current_solution)
        new_obj = self.lateness_calculator.calculate(new)
        if old_obj > new_obj:
            return 1.0
        try:
            return exp((-(new_obj - old_obj)) / self.temperature)
        except OverflowError:
            return 0.0


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
    algo = simulated_annealing(*setup())
    while algo.k < algo.K_MAX:
        algo.step()
    print(algo.best[1], algo.best[0])
