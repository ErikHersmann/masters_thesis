import json
from math import ceil

with open("../../resources/config.json", "r") as f:
    config_dict = json.load(f)


number_of_machines = 3
# must be a list of dicts
machine_qualifications = []
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
print(jobs[0])
# add this urself
with open("../../data_generation/output/seminarset_basic_0.json", "r") as f:
    seminars = json.load(f)


print(jobs)
print(seminars)


current_time = 0
while len(jobs) > 0:
    # Calculate times list for all jobs for all free machines
    all_current_machine_processing_times = []
    currently_free_machines = [machine[-1] for machine in job_order_on_machines if machine[-1]['end_time'] < current_time]
    # Before Seminars
    for machine in currently_free_machines:
        current_machine_processing_times = []
        for job in jobs:
            current_machine_processing_times.append(
                ceil(job["basetime"] / machine_qualifications[job["skill_index"]])
            )
        all_current_machine_processing_times.append(current_machine_processing_times)
    # Recalculate with seminars
    
    # Decide whether to consider seminars ?
    # For each seminar consider the processing times again and if they get less lateness overall plan a seminar


    # If a seminar hasnt been chosen order each machines job processing times by relative speed to baseline
    