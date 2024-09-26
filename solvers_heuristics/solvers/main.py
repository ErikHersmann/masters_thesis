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
        self.jobs = []
        self.BIG_M = sum([job["base_duration"] for job in self.jobs])

    def setup(self):
        self.jobs = []
        self.machines = []
        pass

    def compile(self):
        self.model = LpProblem("Open_Shop", LpMinimize)

        ############
        # VARIABLES#
        ############
        start_times_binary = LpVariable.dicts(
            "x",
            [
                (machine, job, time)
                for machine in range(self.N_MACHINES)
                for job in range(self.N_JOBS)
                for time in range(self.N_TIME)
            ],
            cat="Binary",
        )
        skill_level_binary = LpVariable.dicts(
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
        processing_times = LpVariable.dicts(
            "d",
            [
                (machine, job, time)
                for machine in range(self.N_MACHINES)
                for job in range(self.N_JOBS)
                for time in range(self.N_TIME)
            ],
            cat="Integer",
        )
        machine_one_job_constraint_helper_binary = LpVariable.dicts(
            "a",
            [
                (job1, job2, machine)
                for job1 in range(self.N_JOBS)
                for job2 in range(self.N_JOBS)
                for machine in range(self.N_MACHINES)
            ],
        )
        #####################
        # OBJECTIVE FUNCTION#
        #####################
        lateness = LpVariable("lateness", lowBound=0, cat="Integer")
        for job in range(self.N_JOBS):
            for machine in range(self.N_MACHINES):
                # sum this over t
                time_over_deadline = sum(
                    [
                        time * start_times_binary[(machine, job, time)]
                        + processing_times[(machine, job, time)]
                        - self.jobs[job]["deadline"]
                        for time in range(self.N_TIME)
                    ]
                )
                model += lateness >= time_over_deadline
        model += lateness

        ##############
        # CONSTRAINTS#
        ##############

        # Machines must have at most one job on them for any given time t

        for job1 in range(self.N_JOBS):
            for job2 in range(job1, self.N_JOBS):
                for machine in range(self.N_MACHINES):
                    left_side = sum(
                        [
                            start_times_binary[(machine, job1, time)]
                            * (time + processing_times[(machine, job1, time)])
                            for time in range(self.N_TIME)
                        ]
                    )
                    right_side = sum(
                        [
                            start_times_binary[(machine, job2, time)] * time
                            for time in range(self.N_TIME)
                        ]
                    )
                    model += (
                        left_side
                        - self.BIG_M
                        * (
                            1
                            - machine_one_job_constraint_helper_binary[
                                (job1, job2, machine)
                            ]
                        )
                        <= right_side
                    )
                    # XOR

                    left_side_alt = sum(
                        [
                            start_times_binary[(machine, job2, time)]
                            * (time + processing_times[(machine, job2, time)])
                            for time in range(self.N_TIME)
                        ]
                    )
                    right_side_alt = sum(
                        [
                            start_times_binary[(machine, job1, time)] * time
                            for time in range(self.N_TIME)
                        ]
                    )

                    model += (
                        left_side_alt
                        - self.BIG_M
                        * machine_one_job_constraint_helper_binary[
                            (job1, job2, machine)
                        ]
                        <= right_side_alt
                    )

        # Each job has to be completed, except for seminars which can be completed
        
        

        # Calculate processing durations

        # Set y variables

        # Learning curve helper function

        # Skill level increase only constraint

        # Always skill level greater than zero

    def solve(self):
        pass
