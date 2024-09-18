import json
from random import randint

with open("../resources/config.json", "r") as f:
    config_dict = json.load(f)


if __name__ == "__main__":
    machines = []
    max_growth = config_dict["learning_curves_config"]["maximum_growth"]
    for idx in range(config_dict["number_of_machines"]):
        machines.append(
        #     lambda skill_level, processing_time: int(
        #         skill_level * ((1 + (randint(1, 15) / 100)) ** processing_time)
        #     )
        #     + randint(0, 2)
        # )
        {
            "growth_factor" : 1 + (randint(1,max_growth)/100),
            "growth_const" : randint(0,2)
        }
        )
        # current skill level in w
        # processing time
    # print(" ".join([str(f(1, 5)) for f in machines]))
    with open("output/learning_curveset_0.json", "w") as f:
        json.dump(machines, f)
