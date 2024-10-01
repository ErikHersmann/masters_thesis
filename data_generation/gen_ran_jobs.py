import os.path
from enum import IntEnum
from sys import argv
import random, json


def get_config_dict():
    with open("../resources/config.json", "r") as f:
        return json.load(f)


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


if __name__ == "__main__":
    config_dict = get_config_dict()
    output = []
    try:
        NUM_JOBS = int(argv[1])
    except:
        NUM_JOBS = 3

    first_letter = ord("a")
    last_letter = ord("z")
    for idx in range(NUM_JOBS):
        output.append(
            {
                "skill_required": random.randint(0, len(config_dict["skills"]) - 1),
                "skill_level_required": random.randint(5, 50),
                "base_duration": random.randint(5, 25),
                "deadline": random.randint(20, 100),
                "index": idx,
                "name": "".join(
                    [chr(random.randint(first_letter, last_letter)) for _ in range(10)]
                ),
                "type": "job"
            }
        )

    write_output_without_overwrite(output)
