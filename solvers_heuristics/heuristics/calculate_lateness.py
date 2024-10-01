from sys import argv
import json
from math import ceil

def calculate_lateness(
    order_on_machines: list, machines: list
) -> int:
    """Given a List of Lists of orders of jobs, the jobs and seminars and the machines at t=0
    Calculate the lateness of the given solution (order vectors)

    Args:
        order_on_machines (List of List of int): A list of length N_MACHINES that contains indices that point to jobs or seminars
        machines (List of Dicts with Machine structure): List of machine qualifications and learning curve parameters

    Returns:
        int: The lateness of the given solution
    """
    machine_countdowns = [0 for _ in range(len(machines))]
    lateness = 0
    current_time = 0
    end = False
    while not end:
        machine_countdowns = [max(0, val-1) for val in machine_countdowns]
        if sum([len(order) for order in order_on_machines]) == 0:
            break
        for machine_idx, countdown in enumerate(machine_countdowns):
            if countdown > 0:
                continue
            else:
                current_job = order_on_machines[machine_idx].pop(0)
            # Calculate the processing duration here (if its a non-seminar job)
            if current_job["type"] != "seminar":
                current_processing_duration = ceil(current_job["base_duration"] * (
                    current_job["skill_level_required"]
                    / machines[machine_idx]["skills"][current_job["skill_required"]])
                )
            else:
                current_processing_duration = current_job["base_duration"]
                
            machine_countdowns[machine_idx] = current_processing_duration
            
            lateness += current_time + current_processing_duration - current_job['deadline']
            
            # Update the proficiency of that machine here
            machines[machine_idx]["skills"][current_job["skill_required"]] = (
                machines[machine_idx]["beta"]
                + machines[machine_idx]["alpha"]
                * machines[machine_idx]["skills"][current_job["skill_required"]]
            )
        current_time += 1

    return lateness


if __name__ == "__main__":
    if len(argv) < 2:
        print(f"no path given")
    else:
        path = argv[1]
    with open(path, "r") as f:
        jsonfile = json.load(f)
    print(calculate_lateness(jsonfile['order'], jsonfile['machines']))
