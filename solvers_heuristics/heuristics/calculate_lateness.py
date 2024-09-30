def calculate_lateness(
    order_on_machines: list, jobs_seminars: list, machines: list
) -> int:
    """Given a List of Lists of orders of jobs, the jobs and seminars and the machines at t=0
    Calculate the lateness of the given solution (order vectors)

    Args:
        order_on_machines (List of List of int): A list of lenght N_MACHINES that contains indices that point to jobs or seminars
        jobs_seminars (List of Dicts with Job Structure): List of Jobs and Seminars
        machines (List of Dicts with Machine structure): List of machine qualifications and learning curve parameters

    Returns:
        int: The lateness of the given solution
    """
    machine_countdowns = [0 for _ in range(len(machines))]
    current_time = 0
    end = False
    while not end:
        if sum([len(order) for order in order_on_machines]) == 0:
            break
        for machine_idx, countdown in enumerate(machine_countdowns):
            if countdown > 0:
                continue
            current_job = order_on_machines[machine_idx].pop(0)
            # Calculate the processing duration here (if its a non-seminar job)
            if current_job["type"] != "seminar":
                current_processing_duration = current_job["baseline_duration"] * (
                    current_job["required_skill_level"]
                    / machines[machine_idx]["skills"][current_job["required_skill"]]
                )
            else:
                current_processing_duration = current_job["baseline_duration"]
            machine_countdowns[machine_idx] = current_processing_duration
            # Update the proficiency of that machine here
            machines[machine_idx]["skills"][current_job["required_skill"]] = (
                machines[machine_idx]["beta"]
                + machines[machine_idx]["alpha"]
                * machines[machine_idx]["skills"][current_job["required_skill"]]
            )
        current_time += min([ctdwn for ctdwn in machine_countdowns if ctdwn > 0])
        
        
    return current_time
