from data_generation.gen_ran_jobs import get_config_dict
import json


if __name__ == "__main__":
    config_dict = get_config_dict()
    seminars = []
    for skill_idx, skill in enumerate(config_dict['skills']):
        seminars.append({
            'skill_required': skill_idx,
            'skill_level_required': 0,
            'base_duration': 5,
            'deadline': -1,
            'index': -1,
            'name': "seminar",
            'skill_improvement_baseline': 5
        })
    with open("output/seminarset_basic_0.json", "w") as f:
        json.dump(seminars, f)