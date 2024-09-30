def calculate_lateness(order_on_machines: list, jobs_seminars: list, machines: list) -> int:  
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
    for machine_idx, countdown in enumerate(machine_countdowns):
        if countdown > 0:
            continue
        
    return 0
