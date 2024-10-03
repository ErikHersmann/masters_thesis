from sys import argv
import json
from math import ceil
import pprint


def calculate_lateness(order_on_machines: list, machines: list) -> int:
    """Given a List of Lists of orders of jobs, the jobs and seminars and the machines at t=0
    Calculate the lateness of the given solution (order vectors)

    Args:
        order_on_machines (List of List of int): A list of length N_MACHINES that contains indices that point to jobs or seminars
        machines (List of Dicts with Machine structure): List of machine qualifications and learning curve parameters

    Returns:
        int: The lateness of the given solution
    """
    machine_countdowns = [0 for _ in range(len(order_on_machines))]
    lateness = 0
    current_time = 0
    while True:
        machine_countdowns = [max(0, val - 1) for val in machine_countdowns]
        if sum([len(order) for order in order_on_machines]) == 0:
            break
        for machine_idx, countdown in enumerate(machine_countdowns):
            # print(machine_idx)
            if countdown > 0 or len(order_on_machines[machine_idx]) == 0:
                continue
            else:
                current_job = order_on_machines[machine_idx].pop(0)
            # Calculate the processing duration here (if its a non-seminar job)
            if current_job["type"] != "seminar":
                current_processing_duration = ceil(
                    current_job["base_duration"]
                    * (
                        current_job["skill_level_required"]
                        / machines[machine_idx]["skills"][current_job["skill_required"]]
                    )
                )
            else:
                current_processing_duration = current_job["base_duration"]
            # print(f"m {machine_idx} skill {current_job['skill_required']} level required {current_job['skill_level_required']} machine skill {machines[machine_idx]['skills']}")
            machine_countdowns[machine_idx] = current_processing_duration

            lateness += (
                current_time + current_processing_duration - current_job["deadline"]
            )

            # Update the proficiency of that machine here
            machines[machine_idx]["skills"][current_job["skill_required"]] = (
                machines[machine_idx]["beta"]
                + machines[machine_idx]["alpha"]
                * machines[machine_idx]["skills"][current_job["skill_required"]]
            )
        # print([current_time + m for m in machine_countdowns])
        current_time += 1

    return lateness


if __name__ == "__main__":
    testing = True
    if not testing:
        if len(argv) < 2:
            print(f"no path given")
        else:
            path = argv[1]
        with open(path, "r") as f:
            jsonfile = json.load(f)
        # print(calculate_lateness(jsonfile["order"], jsonfile["machines"]))
    elif testing:
        solutions_path = "results/j5_s1_m2_enumeration.json"
        with open(solutions_path, "r") as f:
            solutions = json.load(f)
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
            if jobs[key]['index'] == -1:
                jobs[key]['index'] = correction_idx
                correction_idx += 1
        
        best = [0]
        
        for row_idx, solution in enumerate(solutions):
            order = [[jobs[idx] for idx in machine] for machine in solution['solution']]
            lateness = calculate_lateness(order, machines)
            solutions[row_idx]['lateness'] = lateness
            if lateness < best[0]:
                best = [lateness, solution]
                print(best)
            
        with open(solutions_path, "w") as f:
            json.dump(solutions, f)
