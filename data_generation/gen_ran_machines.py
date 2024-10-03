import json
from random import randint
from sys import argv

with open("../resources/config.json", "r") as f:
    config_dict = json.load(f)


if __name__ == "__main__":
    if len(argv) < 2:
        N_MACHINES = 3
    else:
        N_MACHINES = int(argv[1])
        
        
    machines = []
    max_growth = config_dict["learning_curves_config"]["maximum_growth"]
    for idx in range(N_MACHINES):
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
            "alpha" : 1 + (randint(1,max_growth)/100),
            "beta" : randint(0,2)
            }
        )
    with open("output/machineset_0.json", "w") as f:
        json.dump(machines, f)
