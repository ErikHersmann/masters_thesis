import json
from random import randint
from sys import argv
from math import floor
import os


def get_config_dict():
    try:
        with open("../resources/config.json", "r") as f:
            config_dict = json.load(f)
    except FileNotFoundError:
        with open("../../resources/config.json", "r") as f:
            config_dict = json.load(f)
    return config_dict


def write_output_without_overwrite(data):
    appendix = 0
    fname_base = "output/machineset_"
    while True:
        cfname = fname_base + str(appendix) + ".json"
        if os.path.isfile(cfname):
            appendix += 1
            continue
        else:
            with open(cfname, "a") as f:
                json.dump(data, f)
            break


def generate_machines(N_MACHINES):
    config_dict = get_config_dict()
    machines = []
    max_growth = config_dict["learning_curves_config"]["maximum_growth"]
    for idx in range(N_MACHINES):
        machines.append(
            {
                "name": "employee #" + str(idx + 1),
                "index": idx,
                "skills": [
                    randint(
                        config_dict["skill_config"]["min_machine_skill"],
                        config_dict["skill_config"]["max_machine_skill"],
                    )
                    for _ in range(len(config_dict["skills"]))
                ],
                "alpha": 1 + (randint(1, max_growth) / 100),
                "beta": randint(0, 2),
                "l_cap": 0
            }
        )
        machines[-1]['l_cap'] = floor((config_dict['skill_config']['max_machine_skill'] / machines[-1]['alpha']) - machines[-1]['beta'])
    return machines


if __name__ == "__main__":
    if len(argv) < 2:
        N_MACHINES = 3
    else:
        N_MACHINES = int(argv[1])
    write_output_without_overwrite(generate_machines(N_MACHINES))
