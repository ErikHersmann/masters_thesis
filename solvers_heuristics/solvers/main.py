import json
from pulp import LpVariable, LpProblem, LpMinimize, GUROBI


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
        self.jobs = None
        self.seminars = None
        self.qualifications = None
        self.BIG_M = sum([job["base_duration"] for job in self.jobs])
        self.lateness = 0

    def skill_range(self):
        """Generate an inclusive range from the lower bound of the skill level up to the upper bound (inclusive)

        Returns:
            Range: The above described range
        """        
        return range(self.SKILL_LEVEL_LB, self.SKILL_LEVEL_UB + 1)

    def setup(self):
        """Sets up jobs, seminars, qualifications, parameters by reading from "../../data_generation" directory
        """        
        self.jobs = []
        self.seminars = []
        self.qualifications = []
        pass

    def solve(self):
        """Instantiates model and solves it
        """        
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
                for level in self.skill_range()(
                    self.SKILL_LEVEL_LB, self.SKILL_LEVEL_UB
                )
                for skill in range(self.N_SKILLS)
            ],
            cat="Binary",
        )
        # Not sure if this is a decision variable
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
                self.model += lateness >= time_over_deadline
        self.model += lateness

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
                    self.model += (
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

                    self.model += (
                        left_side_alt
                        - self.BIG_M
                        * machine_one_job_constraint_helper_binary[
                            (job1, job2, machine)
                        ]
                        <= right_side_alt
                    )

        # Each job has to be completed once

        for job in self.jobs:
            self.model += (
                sum(
                    [
                        start_times_binary[(machine, job, time)]
                        for machine in range(self.N_MACHINES)
                        for time in range(self.N_TIME)
                    ]
                )
                == 1
            )

        # Seminars can be completed at most once
        for machine in range(self.N_MACHINES):
            for seminar in self.seminars:
                self.model += (
                    sum(
                        [
                            start_times_binary[(machine, seminar, time)]
                            for time in range(self.N_TIME)
                        ]
                    )
                    <= 1
                )

        # Calculate processing durations

        for job_index in range(self.N_JOBS):
            current_job = self.jobs[job_index]
            for machine in range(self.N_MACHINES):
                for time in range(self.N_TIME):
                    self.model += processing_times[(machine, job_index, time)] == sum(
                        [
                            sum(
                                [
                                    skill_level_binary[(machine, time, level, skill)]
                                    * (
                                        (
                                            current_job["skill_level_required"]
                                            * current_job["base_duration"]
                                        )
                                        / skill
                                    )
                                    for level in self.skill_range()
                                ]
                            )
                            for skill in range(self.N_SKILLS)
                        ]
                    )

        # Set y variables (also uses helper function)

        for machine in range(self.N_MACHINES):
            for job in range(self.N_JOBS):
                for skill in range(self.N_SKILLS):
                    for time in range(self.N_TIME):
                        self.model += (
                            skill_level_binary[
                                (
                                    machine,
                                    time + 1,
                                    min(learning_curve_function(machine, time, skill), self.SKILL_LEVEL_UB),
                                    skill,
                                )
                            ]
                            == 1
                        )

        # Learning curve helper function

        def learning_curve_function(machine, time, skill):
            left_side = sum(
                [
                    start_times_binary[(machine, job_index, time)]
                    * (
                        self.qualifications[machine]["beta"]
                        + self.qualifications[machine]["alpha"]
                        * sum(
                            [
                                level
                                * skill_level_binary[
                                    (
                                        machine,
                                        time,
                                        level,
                                        self.jobs[job_index]["skill_required"],
                                    )
                                ]
                                for level in self.skill_range()
                            ]
                        )
                    )
                    for job_index in self.N_JOBS
                ]
            )
            right_side = sum(
                [
                    level * skill_level_binary[(machine, time, level, skill)]
                    for level in self.skill_range()
                ]
            )
            return max(left_side, right_side)

        # Skill level increase only constraint

        for machine in range(self.N_MACHINES):
            for time in range(1, self.N_TIME):
                for skill in range(self.N_SKILLS):
                    left_side = sum(
                        [
                            level * skill_level_binary[(machine, time, level, skill)]
                            for level in self.skill_range()
                        ]
                    )
                    right_side = sum(
                        [
                            level
                            * skill_level_binary[(machine, time - 1, level, skill)]
                            for level in self.skill_range()
                        ]
                    )
                    self.model += left_side >= right_side

        # Skill level greater than zero

        for machine in range(self.N_MACHINES):
            for skill in range(self.N_SKILLS):
                self.model += (
                    sum(
                        [
                            skill_level_binary[(machine, 0, level, skill)]
                            for level in self.skill_range()
                        ]
                    )
                    == 1
                )

        ######################
        # SOLVING WITH GUROBI#
        ######################

        self.model.solve(
            GUROBI(
                mip=True,
                logPath="../../resources/results/gurobi_log.txt",
                timeLimit=30,
                displayInterval=5,
            )
        )
        self.lateness = lateness.varValue

        #############################
        # EXTRACTING VARIABLE VALUES#
        #############################

        results = {}

        results["start_times_binary"] = [
            index for index, var in start_times_binary.items() if var.value() == 1
        ]

        results["skill_level_binary"] = [
            index for index, var in skill_level_binary.items() if var.value() == 1
        ]

        results["processing_times"] = {
            str(index): var.value() for index, var in processing_times.items()
        }

        results["machine_one_job_constraint_helper_binary"] = [
            index
            for index, var in machine_one_job_constraint_helper_binary.items()
            if var.value() == 1
        ]

        with open("../../resources/results/variable_values_debug.json", "w") as f:
            json.dump(results, f, indent=4)



if __name__ == "__main__":
    solver = linear_solver(verbose=True)
    solver.setup()
    #solver.solve()