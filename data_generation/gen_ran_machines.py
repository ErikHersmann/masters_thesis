import json
from random import randint

with open("../resources/config.json", "r") as f:
    config_dict = json.load(f)


if __name__ == "__main__":
    machines = []
    for idx in range(config_dict["number_of_machines"]):
        machines.append(
            {
                "name": "employee #" + str(idx+1),
                "index": idx,
                "skills": [
                    randint(
                        config_dict["skill_config"]["min_machine_skill"],
                        config_dict["skill_config"]["max_machine_skill"],
                    )
                    for _ in range(len(config_dict["skills"]))
                ],
            }
        )
    with open("output/machineset_0.json", "w") as f:
        json.dump(machines, f)
