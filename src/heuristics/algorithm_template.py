import json
from calculate_lateness import calculate_lateness

class heuristic_template():
    def __init__(self, machines, jobs_seminars) -> None:
        with open("../../resources/config.json", "r") as f:
            self.config = json.load(f)

        self.N_JOBS = sum([1 for x in jobs_seminars if x["type"] == "job"])
        self.N_SEMINARS = sum([1 for x in jobs_seminars if x["type"] == "seminar"])
        self.N_MACHINES = len(machines)
        self.lateness_calculator = calculate_lateness(machines, jobs_seminars)
