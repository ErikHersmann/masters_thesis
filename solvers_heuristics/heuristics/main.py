import json
from enum import IntEnum

with open("../../resources/config.json", "r") as f:
    config_dict = json.load(f)


number_of_machines = 3
machines_array = [[] for _ in range(number_of_machines)]
Skills = IntEnum('Skills', ['C_Plus_Plus', 'C_Sharp', 'Python', 'Ruby', 'Office', 'Communication'])

# this should come from a file or generator function and contain tuples like this
# single_job = {'skill_required': Skills.C_Sharp,
#               'skill_level_required': 5,
#               'base_duration': 20,
#               'deadline': 40}
jobs = []
# add this urself
seminars = []

jobs += seminars

current_time = 0



