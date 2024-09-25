import json
from pulp import LpVariable, LpProblem, LpMinimize


def irange(start, end):
    return range(start, end + 1)


class linear_solver:
    def __init__(self, verbose=False) -> None:
        self.model = None
        self.runtime = None
        with open("../../resources/config.json", "r") as f:
            self.config_dict = json.load(f)
        self.verbose = verbose
        self.N_JOBS = self.config_dict["number_of_jobs"]
        self.N_MACHINES = self.config_dict["number_of_machines"]
        self.N_TIME = self.config_dict["max_time"]
        self.SKILL_LEVEL_LB = self.config_dict["skill_config"]["min_machine_skill"]
        self.SKILL_LEVEL_UB = self.config_dict["skill_config"]["max_machine_skill"]
        self.SKILLS = self.config_dict["skills"]
        self.N_SKILLS = len(self.SKILLS)

    def compile(self):
        self.model = LpProblem("Open_Shop", LpMinimize)

        ############
        # VARIABLES#
        ############
        start_times = LpVariable.dicts(
            "x",
            [
                (machine, job, time)
                for machine in range(self.N_MACHINES)
                for job in range(self.N_JOBS)
                for time in range(self.N_TIME)
            ],
            cat="Binary",
        )
        skill_level = LpVariable.dicts(
            "y",
            [
                (machine, time, level, skill)
                for machine in range(self.N_MACHINES)
                for time in range(self.N_TIME)
                for level in irange(self.SKILL_LEVEL_LB, self.SKILL_LEVEL_UB)
                for skill in range(self.N_SKILLS)
            ],
            cat="Binary",
        )

    def solve(self):
        pass
