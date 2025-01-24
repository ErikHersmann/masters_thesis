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
    fname_base = f"output/m{len(data)}_"
    while True:
        cfname = fname_base + str(appendix) + ".json"
        if os.path.isfile(cfname):
            appendix += 1
            continue
        else:
            with open(cfname, "a") as f:
                json.dump(data, f)
            break


def generate_machines(N_MACHINES, config_dict):
    machines = []
    alpha_min = config_dict["learning_curves_config"]["alpha_min"]
    alpha_max = config_dict["learning_curves_config"]["alpha_max"]
    beta_min = config_dict["learning_curves_config"]["beta_min"]
    beta_max = config_dict["learning_curves_config"]["beta_max"]
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
                "alpha": randint(alpha_min, alpha_max),
                "beta": randint(beta_min, beta_max),
                "l_cap": 0
            }
        )
        machines[-1]["l_cap"] = floor(
            machines[-1]["alpha"] * machines[-1]["beta"] + machines[-1]["alpha"]
        )
    return machines


if __name__ == "__main__":
    if len(argv) < 2:
        N_MACHINES = 3
    else:
        N_MACHINES = int(argv[1])
    write_output_without_overwrite(generate_machines(N_MACHINES, get_config_dict()))
