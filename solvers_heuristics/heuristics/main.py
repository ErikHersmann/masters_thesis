import json

with open("../../resources/config.json", "r") as f:
    config_dict = json.load(f)


number_of_machines = 3
machines_array = [[] for _ in range(number_of_machines)]




# this should come from a file or generator function and contain tuples like this
# single_job = {'skill_required': Skills.C_Sharp,
#               'skill_level_required': 5,
#               'base_duration': 20,
#               'deadline': 40,
#               'index': 0,
#               'name': "performance benchmarking",
#              }
with open('../../data_generation/output/jobset_0.json', 'r') as f:
    jobs = json.load(f)
print(jobs[0])
# add this urself
with open('../../data_generation/output/seminarset_basic_0.json', 'r') as f:
    seminars = json.load(f)

jobs += seminars

print(jobs)

current_time = 0



