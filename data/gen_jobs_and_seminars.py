import os
from enum import IntEnum
from sys import argv
import random, json


def get_config_dict():
    try:
        with open("../resources/config.json", "r") as f:
            config_dict = json.load(f)
    except FileNotFoundError:
        with open("../../resources/config.json", "r") as f:
            config_dict = json.load(f)
    return config_dict


def write_output_without_overwrite(data, index_tuple):
    appendix = 0
    n_job, n_sem = index_tuple
    fname_base = f"output/j{n_job}s{n_sem}_"
    while True:
        cfname = fname_base + str(appendix) + ".json"
        if os.path.isfile(cfname):
            appendix += 1
            continue
        else:
            with open(cfname, "a") as f:
                json.dump(data, f)
            print(f"wrote to {cfname}")
            break

def generate_jobs_seminars(NUM_JOBS, config_dict, NUM_SEMINARS=None):
    output = []
    first_letter = ord("a")
    last_letter = ord("z")
    for idx in range(NUM_JOBS):
        output.append(
            {
                "skill_required": random.randint(0, len(config_dict["skills"]) - 1),
                "skill_level_required": random.randint(
                    config_dict["skill_config"]["min_job_requirement"],
                    config_dict["skill_config"]["max_job_requirement"],
                ),
                "base_duration": random.randint(3, 15),
                "deadline": random.randint(3, 100),
                "index": idx,
                "name": "".join(
                    [chr(random.randint(first_letter, last_letter)) for _ in range(5)]
                ),
                "type": "job",
            }
        )
    if NUM_SEMINARS:
        skill_count = NUM_SEMINARS
    else:
        skill_count = len(config_dict['skills'])
    for skill_idx in range(skill_count):
        output.append(
            {
                "skill_required": skill_idx,
                "skill_level_required": 0,
                "base_duration": 5,
                "deadline": None,
                "index": idx + 1 + skill_idx,
                "name": f"seminar skill #{skill_idx}",
                "skill_improvement_baseline": 5,
                "type": "seminar",
            }
        )
    return output


if __name__ == "__main__":
    try:
        NUM_JOBS = int(argv[1])
    except:
        NUM_JOBS = 5
        print(f"no job count specified continuing with default {NUM_JOBS}")
    output = generate_jobs_seminars(NUM_JOBS, get_config_dict())
    write_output_without_overwrite(output, (NUM_JOBS, len(output)-NUM_JOBS))
