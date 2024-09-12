import os.path
from enum import IntEnum
from sys import argv
import random, json


with open("../resources/config.json", "r") as f:
    config_dict = json.load(f)

def write_output_without_overwrite(data):
    appendix = 0
    fname_base = "output/jobset_"
    while True:
        cfname = fname_base + str(appendix) + ".json"
        if os.path.isfile(cfname):
            appendix += 1
            continue
        else:
            with open(cfname, "a") as f:
                json.dump(data, f)
            break


output = []
try:
    NUM_JOBS = int(argv[1])
except:
    NUM_JOBS = 3


for idx in range(NUM_JOBS):
    output.append(
        {
            "skill_required": random.randint(0, len(config_dict['skills'])-1),
            "skill_level_required": random.randint(0, 50),
            "base_duration": random.randint(5, 25),
            "deadline": random.randint(20, 100),
            "index": idx,
            "name": "".join(
                [
                    chr(i)
                    for i in [random.randint(ord("a"), ord("z")) for _ in range(10)]
                ]
            ),
        }
    )
    
    
write_output_without_overwrite(output)
