import json
from math import ceil


def dprint(dictionary_list, name):
    """Helper function to pretty print the list of dictionaries

    Args:
        dictionary_list (list of dictionaries): A list of dictionaries (of similar or same structure)
        name (String): Name of the dictionar structure (for printing)
    """
    print(f"{name}\n")
    for row in dictionary_list:
        print(row)
    print()


def sort_jobs_by_priority(jobs_list, mode=0):
    """Sorts the available jobs according to a rule specified in mode

    Args:
        jobs_list (List of dictionaries): A list of dictionaries (of the job structure) refer to the generator scripts for a sample
        mode (int, optional): A mode that specifies the rule according to which the jobs are supposed to be sorted. Defaults to 0.

    Returns:
        List of dictionaries: Returns the jobs_list sorted according to the specified mode
    """
    match mode:
        case 0:
            return enumerate(jobs_list)
        case 1:
            return sorted(enumerate(jobs_list), key=lambda x: x[1]["deadline"])


def calculate_lateness(job_order_on_machines):
    lateness = 0
    for machine in job_order_on_machines:
        for job in machine:
            lateness += job["end_time"] - job["deadline"]
    return lateness


def greedy_job_assignment(
    all_current_machine_processing_times, jobs, job_order_on_machines, current_time, learning_curves, machine_qualifications
):
    print(f"current machine processing time {all_current_machine_processing_times}\n")
    machines_used_in_this_iteration = []
    for job_index, job in sort_jobs_by_priority(jobs, 1):
        # find the machine that has the shortest processing time for the current job
        if len(machines_used_in_this_iteration) == len(
            all_current_machine_processing_times
        ):
            break
        best_machine_idx = sorted(
            [
                machine
                for machine in all_current_machine_processing_times
                if machine[0] not in machines_used_in_this_iteration
            ],
            key=lambda x: x[1][job_index],
            reverse=True,
        )[-1][0]
        # plan the job on that machine and dont consider it for the next few jobs
        job_order_on_machines[best_machine_idx].append(job)
        job_order_on_machines[best_machine_idx][-1]["start_time"] = current_time
        job_order_on_machines[best_machine_idx][-1]["end_time"] = (
            current_time
            + [
                processing_time
                for processing_time in all_current_machine_processing_times
                if processing_time[0] == best_machine_idx
            ][0][1][job_index]
        )

        jobs.remove(job)
        machines_used_in_this_iteration.append(best_machine_idx)
        # break


def get_current_machine_processing_times(job_order_on_machines, jobs, current_time):
    all_current_machine_processing_times = []
    # Get the last job on all machines whose finish time (on that job) is less than the current time
    currently_free_machines = [
        idx
        for idx, machine in enumerate(job_order_on_machines)
        if len(machine) == 0 or machine[-1]["end_time"] < current_time
    ]
    print(f"t={current_time}\tFree machines\t{currently_free_machines}\n")
    # Before Seminars
    for machine in currently_free_machines:
        current_machine_processing_times = []
        for job in jobs:
            # Calculate the new processing time (Maybe use a function here to allow for changing this later however this shouldn't be too much of an issue 問題ない)
            current_machine_processing_times.append(
                ceil(
                    job["base_duration"]
                    * (
                        job["skill_level_required"]
                        / machine_qualifications[machine]["skills"][
                            job["skill_required"]
                        ]
                    )
                )
            )
        all_current_machine_processing_times.append(
            (machine, current_machine_processing_times)
        )
    return all_current_machine_processing_times


def calculate_lateness_next_step():
    return 0


########
# SETUP#
########

with open("../../resources/config.json", "r") as f:
    config_dict = json.load(f)


number_of_machines = config_dict["number_of_machines"]
# must be a list of dicts
job_order_on_machines = [[] for _ in range(number_of_machines)]


# this should come from a file or generator function and contain tuples like this
# single_job = {'skill_required': Skills.C_Sharp,
#               'skill_level_required': 5,
#               'base_duration': 20,
#               'deadline': 40,
#               'index': 0,
#               'name': "performance benchmarking",
#              }
with open("../../data_generation/output/jobset_0.json", "r") as f:
    jobs = json.load(f)
# add this urself
with open("../../data_generation/output/seminarset_basic_0.json", "r") as f:
    seminars = json.load(f)
with open("../../data_generation/output/machineset_0.json", "r") as f:
    machine_qualifications = json.load(f)
with open("../../data_generation/output/learning_curveset_0.json") as f:
    learning_curves = json.load(f)
    learning_curves = [
        lambda skill_level, processing_time: int(
            skill_level * (machine["growth_factor"] ** processing_time)
        )
        + machine["growth_const"]
        for machine in learning_curves
    ]


dprint(jobs, "Jobs")
dprint(seminars, "Seminars")
dprint(machine_qualifications, "Machines")


############
# MAIN LOOP#
############

current_time = 0
while len(jobs) > 0:
    # Calculate times list for all jobs for all free machines
    all_current_machine_processing_times = get_current_machine_processing_times(
        job_order_on_machines, jobs, current_time
    )
    # Calculate the lateness of the jobs in the next step
    pre_seminar_lateness = calculate_lateness_next_step()
    # Recalculate with seminars
    post_seminar_lateness = calculate_lateness_next_step()

    if post_seminar_lateness < pre_seminar_lateness:
        pass

    # Greedily pick the earliest deadline jobs and the fastest worker on them ?
    greedy_job_assignment(
        all_current_machine_processing_times, jobs, job_order_on_machines, current_time, learning_curves
    )

    dprint(job_order_on_machines, "Order")
    current_time = (
        min(
            [job_on_machine[-1]["end_time"] for job_on_machine in job_order_on_machines]
        )
        + 1
    )


##########
# RESULTS#
##########

print(calculate_lateness(job_order_on_machines))
