from sys import argv
import json
from math import ceil
from pprint import pprint
from copy import deepcopy


# Replace with config dict
with open("../../resources/config.json", "r") as f:
    config = json.load(f)
SKILL_LIMIT_UB = config["skill_config"]["max_machine_skill"]


class calculate_lateness:
    def __init__(self, machines, jobs_seminars) -> None:
        self.machines = machines
        self.jobs_seminars = jobs_seminars
        with open("../../resources/config.json", "r") as f:
            config = json.load(f)
        self.SKILL_LIMIT_UB = config["skill_config"]["max_machine_skill"]

    def calculate(self, order):
        """Given a List of Lists of orders of jobs (with details of each job/seminar), and the machines at t=0
        Calculate the lateness of the given solution (order vectors)

        Args:
            order_on_machines (List of List of int): A list of length N_MACHINES that contains indices that point to jobs or seminars
            machines (List of Dicts with Machine structure): List of machine qualifications and learning curve parameters

        Returns:
            int: The lateness of the given solution
        """
        order = [[self.jobs_seminars[idx] for idx in machine] for machine in order]
        machines = deepcopy(self.machines)
        lateness = None

        ###########
        # MACHINES#
        ###########
        for machine_idx in range(len(machines)):
            current_time = 0
            #######
            # JOBS#
            #######
            while len(order[machine_idx]) > 0:
                current_job = order[machine_idx].pop(0)
                if current_job["type"] != "seminar":
                    current_processing_duration = ceil(
                        current_job["base_duration"]
                        * (
                            current_job["skill_level_required"]
                            / machines[machine_idx]["skills"][
                                current_job["skill_required"]
                            ]
                        )
                    )
                    current_lateness_term = (
                        current_time
                        + current_processing_duration
                        - current_job["deadline"]
                    )
                    if not lateness or current_lateness_term > lateness:
                        lateness = current_lateness_term

                    # print(f"t {current_time} machine {machine_idx} lateness {lateness} others {current_time} {current_processing_duration} {current_job['deadline']}")

                else:
                    current_processing_duration = current_job["base_duration"]

                machines[machine_idx]["skills"][current_job["skill_required"]] = min(
                    (
                        machines[machine_idx]["beta"]
                        + machines[machine_idx]["alpha"]
                        * machines[machine_idx]["skills"][current_job["skill_required"]]
                    ),
                    self.SKILL_LIMIT_UB,
                )
                current_time += current_processing_duration
        return lateness


if __name__ == "__main__":
    ##############################
    # TESTING ON FULL ENUMERATION#
    ##############################
    solutions_path = "results/j5_s2_m2_enumeration.json"
    with open(solutions_path, "r") as f:
        solutions = json.load(f)
    with open("../../data/output/machineset_1.json", "r") as f:
        machines = json.load(f)
    with open("../../data/output/jobset_j5_s2.json", "r") as f:
        jobs = json.load(f)
    calculator = calculate_lateness(machines, jobs)
    best = [0]
    for row_idx, solution in enumerate(solutions):
        lateness = calculator.calculate(solution["solution"])
        solutions[row_idx]["lateness"] = lateness
        if lateness < best[0]:
            best = [lateness, solution]
    print(best)
    with open(solutions_path, "w") as f:
        json.dump(solutions, f)
