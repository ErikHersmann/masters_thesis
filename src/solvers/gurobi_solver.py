import json, os
from pulp import LpVariable, LpProblem, LpMinimize, GUROBI


class linear_solver:

    def __init__(self, machines, jobs_seminars, config_dict, verbose=False) -> None:
        self.RESULTS_DIR = "results/"
        self.config_dict = config_dict
        self.verbose = verbose
        self.N_TIME = self.config_dict["max_time"]
        self.SKILL_LEVEL_LB = self.config_dict["skill_config"]["min_machine_skill"]
        self.SKILL_LEVEL_UB = self.config_dict["skill_config"]["max_machine_skill"]
        self.SKILLS = self.config_dict["skills"]
        self.N_SKILLS = len(self.SKILLS)
        self.PROCESSING_TIMES_UB = 100
        self.ALMOST_ONE = 0.999
        self.machines = machines
        self.jobs_seminars = jobs_seminars
        self.BIG_M_XOR = sum([job["base_duration"] for job in self.jobs_seminars])
        # Calculate this from the worst skilled employee at the longest job instead
        self.BIG_M_CAP = 10000
        self.BIG_M_MAX = 10000
        self.N_MACHINES = len(self.machines)
        self.N_JOBS = sum([1 for x in self.jobs_seminars if x["type"] == "job"])
        self.N_SEMINARS = sum(
            [1 for x in self.jobs_seminars if x["type"] == "seminars"]
        )
        self.N_JOBS_AND_SEMINARS = len(self.jobs_seminars)
        if self.verbose:
            print(
                f"Jobs {self.N_JOBS} Machines {self.N_MACHINES} Skills {self.N_SKILLS} Time {self.N_TIME} Level {self.SKILL_LEVEL_UB-self.SKILL_LEVEL_LB} Product {self.N_JOBS*self.N_MACHINES*self.N_TIME*self.N_SKILLS*(self.SKILL_LEVEL_UB-self.SKILL_LEVEL_LB)}"
            )

    def skill_range(self):
        """Generate an inclusive range from the lower bound of the skill level up to the upper bound (inclusive)

        Returns:
            Range: The above described range
        """
        return range(self.SKILL_LEVEL_LB, self.SKILL_LEVEL_UB + 1)

    def pre_compile(self):
        """Instantiates the model istance and the variables"""
        self.model = LpProblem("Human_Resource_Scheduling", LpMinimize)

        ############
        # VARIABLES#
        ############
        self.machine_one_job_constraint_helper_binary = LpVariable.dicts(
            "a",
            [
                (job1, job2, machine)
                for job1 in range(self.N_JOBS_AND_SEMINARS)
                for job2 in range(self.N_JOBS_AND_SEMINARS)
                for machine in range(self.N_MACHINES)
            ],
            cat="Binary",
        )
        self.start_cdot_duration_helper_binary = LpVariable.dicts(
            "b",
            [
                (machine, job, time)
                for machine in range(self.N_MACHINES)
                for job in range(self.N_JOBS_AND_SEMINARS)
                for time in range(self.N_TIME)
            ],
            cat="Binary",
        )
        self.skill_increased_helper_binary = LpVariable.dicts(
            "d",
            [
                (machine, time, skill)
                for machine in range(self.N_MACHINES)
                for time in range(self.N_TIME)
                for skill in range(self.N_SKILLS)
            ],
            cat="Binary",
        )
        self.start_cdot_skill_level_helper_binary = LpVariable.dicts(
            "e",
            [
                (machine, job, time, level, skill)
                for machine in range(self.N_MACHINES)
                for job in range(self.N_JOBS_AND_SEMINARS)
                for time in range(self.N_TIME)
                for level in self.skill_range()
                for skill in range(self.N_SKILLS)
            ],
            cat="Binary",
        )
        self.processing_times_integer = LpVariable.dicts(
            "p",
            [
                (machine, job, time)
                for machine in range(self.N_MACHINES)
                for job in range(self.N_JOBS_AND_SEMINARS)
                for time in range(self.N_TIME)
            ],
            cat="Integer",
            lowBound=0,
            upBound=500,
        )
        self.start_times_binary = LpVariable.dicts(
            "x",
            [
                (machine, job, time)
                for machine in range(self.N_MACHINES)
                for job in range(self.N_JOBS_AND_SEMINARS)
                for time in range(self.N_TIME)
            ],
            cat="Binary",
        )
        self.skill_level_binary = LpVariable.dicts(
            "y",
            [
                (machine, time, level, skill)
                for machine in range(self.N_MACHINES)
                for time in range(self.N_TIME)
                for level in self.skill_range()
                for skill in range(self.N_SKILLS)
            ],
            cat="Binary",
        )

    def compile(self):
        """Adds the constraints to the model"""
        self.pre_compile()
        #####################
        # OBJECTIVE FUNCTION#
        #####################

        # Lateness is the sum of differences between end time - Deadline for all jobs

        lb_lateness = -max([job["deadline"] for job in self.jobs_seminars])
        print(f"lb lateness {lb_lateness}")
        self.lateness = LpVariable(
            "lateness",
            lowBound=lb_lateness,
            cat="Integer",
        )
        for job in range(self.N_JOBS):
            for machine in range(self.N_MACHINES):
                time_over_deadline = sum(
                    [
                        time * self.start_times_binary[(machine, job, time)]
                        + self.start_cdot_duration_helper_binary[(machine, job, time)]
                        - (
                            self.jobs_seminars[job]["deadline"]
                            * self.start_times_binary[(machine, job, time)]
                        )
                        for time in range(self.N_TIME)
                    ]
                )
                self.model += self.lateness >= time_over_deadline
        self.model += self.lateness

        ##############
        # CONSTRAINTS#
        ##############

        # Each job has to be completed once

        for job in range(self.N_JOBS):
            self.model += (
                sum(
                    [
                        self.start_times_binary[(machine, job, time)]
                        for machine in range(self.N_MACHINES)
                        for time in range(self.N_TIME)
                    ]
                )
                == 1
            )

        # Seminars can be completed at most once
        for machine in range(self.N_MACHINES):
            for seminar in range(self.N_JOBS, self.N_JOBS_AND_SEMINARS):
                self.model += (
                    sum(
                        [
                            self.start_times_binary[(machine, seminar, time)]
                            for time in range(self.N_TIME)
                        ]
                    )
                    <= 1
                )

        # Machines must have at most one job on them for any given time t

        for job1 in range(self.N_JOBS_AND_SEMINARS):
            for job2 in range(self.N_JOBS_AND_SEMINARS):
                if job1 == job2:
                    continue
                for machine in range(self.N_MACHINES):
                    left_side = sum(
                        [
                            self.start_times_binary[(machine, job1, time)] * time
                            + self.start_cdot_duration_helper_binary[
                                (machine, job1, time)
                            ]
                            for time in range(self.N_TIME)
                        ]
                    )
                    right_side = sum(
                        [
                            self.start_times_binary[(machine, job2, time)] * time
                            for time in range(self.N_TIME)
                        ]
                    )
                    self.model += (
                        left_side
                        - self.BIG_M_XOR
                        * (
                            1
                            - self.machine_one_job_constraint_helper_binary[
                                (job1, job2, machine)
                            ]
                        )
                        <= right_side
                    )
                    # XOR

                    left_side_alt = sum(
                        [
                            self.start_times_binary[(machine, job2, time)] * time
                            + self.start_cdot_duration_helper_binary[
                                (machine, job2, time)
                            ]
                            for time in range(self.N_TIME)
                        ]
                    )
                    right_side_alt = sum(
                        [
                            self.start_times_binary[(machine, job1, time)] * time
                            for time in range(self.N_TIME)
                        ]
                    )

                    self.model += (
                        left_side_alt
                        - self.BIG_M_XOR
                        * self.machine_one_job_constraint_helper_binary[
                            (job1, job2, machine)
                        ]
                        <= right_side_alt
                    )

        # # Helper variable that models the multiplication constraints

        for machine in range(self.N_MACHINES):
            for job in range(self.N_JOBS_AND_SEMINARS):
                for time in range(self.N_TIME):
                    self.model += (
                        self.start_cdot_duration_helper_binary[(machine, job, time)]
                        <= self.start_times_binary[(machine, job, time)]
                        * self.BIG_M_CAP
                    )
                    self.model += (
                        self.start_cdot_duration_helper_binary[(machine, job, time)]
                        >= 0
                    )
                    # INFEASIBLE

                    # self.model += (
                    # self.start_cdot_duration_helper_binary[(machine, job, time)]
                    # <= self.processing_times_integer[(machine, job, time)]
                    # )
                    # self.model += (
                    # self.start_cdot_duration_helper_binary[(machine, job, time)]
                    # >= self.processing_times_integer[(machine, job, time)]
                    # - (1 - self.start_times_binary[(machine, job, time)])
                    # * self.BIG_M_CAP
                    # )

        # Calculate processing durations

        for job_index in range(self.N_JOBS):
            current_job = self.jobs_seminars[job_index]
            current_job_term = (
                current_job["skill_level_required"] * current_job["base_duration"]
            )
            for machine in range(self.N_MACHINES):
                for time in range(self.N_TIME - 1):
                    right_side_term = sum(
                        [
                            self.skill_level_binary[
                                (machine, time, level, current_job["skill_required"])
                            ]
                            * (current_job_term / level)
                            for level in self.skill_range()
                        ]
                    )

                    self.model += (
                        self.processing_times_integer[(machine, job_index, time)]
                        >= right_side_term
                    )
                    self.model += (
                        self.processing_times_integer[(machine, job_index, time)]
                        <= self.ALMOST_ONE + right_side_term
                    )

        # Calculation of processing durations of seminars

        for seminar_index in range(self.N_JOBS, self.N_JOBS_AND_SEMINARS):
            for machine_idx in range(self.N_MACHINES):
                for time_idx in range(self.N_TIME):
                    self.model += (
                        self.processing_times_integer[
                            (machine_idx, seminar_index, time_idx)
                        ]
                        == self.jobs_seminars[seminar_index]["base_duration"]
                    )

        # Skill level increase only constraint

        for machine_idx in range(self.N_MACHINES):
            for time_idx in range(1, self.N_TIME):
                for skill_idx in range(self.N_SKILLS):
                    left_side = sum(
                        [
                            level
                            * self.skill_level_binary[
                                (machine_idx, time_idx, level, skill_idx)
                            ]
                            for level in self.skill_range()
                        ]
                    )
                    right_side = sum(
                        [
                            level
                            * self.skill_level_binary[
                                (machine_idx, time_idx - 1, level, skill_idx)
                            ]
                            for level in self.skill_range()
                        ]
                    )
                    self.model += left_side >= right_side

        # Skill level at start constraint

        for machine_idx in range(self.N_MACHINES):
            for skill_idx in range(self.N_SKILLS):
                self.model += (
                    self.skill_level_binary[
                        (
                            machine_idx,
                            0,
                            self.machines[machine]["skills"][skill_idx],
                            skill_idx,
                        )
                    ]
                    == 1
                )

        # An employee should always only possess one level for a given skill

        for machine_idx in range(self.N_MACHINES):
            for skill_idx in range(self.N_SKILLS):
                for time_idx in range(self.N_TIME):
                    self.model += (
                        sum(
                            [
                                self.skill_level_binary[
                                    (
                                        machine_idx,
                                        time_idx,
                                        level,
                                        skill_idx,
                                    )
                                ]
                                for level in self.skill_range()
                            ]
                        )
                    ) == 1

        ##################################################################
        # Constraints for the skill level index integer decision variable#
        ##################################################################

        for machine_idx in range(self.N_MACHINES):
            alpha = self.machines[machine_idx]["alpha"]
            beta = self.machines[machine_idx]["beta"]
            l_cap = self.machines[machine_idx]["l_cap"]
            for time_idx in range(self.N_TIME - 1):
                for skill_idx in range(self.N_SKILLS):
                    right_side = sum(
                        [
                            beta
                            * self.start_times_binary[
                                (machine_idx, job_index, time_idx)
                            ]
                            + alpha
                            * sum(
                                [
                                    level
                                    * self.start_cdot_skill_level_helper_binary[
                                        (
                                            machine_idx,
                                            job_index,
                                            time_idx,
                                            level,
                                            skill_idx,
                                        )
                                    ]
                                    for level in range(self.SKILL_LEVEL_LB, l_cap)
                                ]
                            )
                            for job_index in range(self.N_JOBS_AND_SEMINARS)
                        ]
                    )
                    old_level = sum(
                        [
                            level
                            * self.skill_level_binary[
                                (machine_idx, time_idx, level, skill_idx)
                            ]
                            for level in self.skill_range()
                        ]
                    )
                    # should be bigger or equal the new level or 0
                    self.model += (
                        sum(
                            [
                                level
                                * self.skill_level_binary[
                                    (
                                        machine_idx,
                                        time_idx + 1,
                                        level,
                                        skill_idx,
                                    )
                                ]
                                for level in self.skill_range()
                            ]
                        )
                        >= right_side
                    )
                    # should always be bigger or equal the old level
                    self.model += (
                        sum(
                            [
                                level
                                * self.skill_level_binary[
                                    (
                                        machine_idx,
                                        time_idx + 1,
                                        level,
                                        skill_idx,
                                    )
                                ]
                                for level in self.skill_range()
                            ]
                        )
                        >= old_level
                    )
                    # should be smaller or equal to the new level if d = 0
                    self.model += (
                        sum(
                            [
                                level
                                * self.skill_level_binary[
                                    (
                                        machine_idx,
                                        time_idx + 1,
                                        level,
                                        skill_idx,
                                    )
                                ]
                                for level in self.skill_range()
                            ]
                        )
                        <= self.BIG_M_MAX
                        * self.skill_increased_helper_binary[
                            (machine_idx, time_idx, skill_idx)
                        ]
                        + right_side
                    )
                    # should be smaller or equal to the old level if d = 1
                    self.model += (
                        sum(
                            [
                                level
                                * self.skill_level_binary[
                                    (
                                        machine_idx,
                                        time_idx + 1,
                                        level,
                                        skill_idx,
                                    )
                                ]
                                for level in self.skill_range()
                            ]
                        )
                        <= self.BIG_M_MAX
                        * (
                            1
                            - self.skill_increased_helper_binary[
                                (machine_idx, time_idx, skill_idx)
                            ]
                        )
                        + old_level
                    )

        # # Constraints for multiplication helper variable

        for machine_idx in range(self.N_MACHINES):
            for job_idx in range(self.N_JOBS_AND_SEMINARS):
                for time_idx in range(self.N_TIME):
                    for level in self.skill_range():
                        for skill_idx in range(self.N_SKILLS):
                            self.model += (
                                self.start_cdot_skill_level_helper_binary[
                                    (machine_idx, job_idx, time_idx, level, skill_idx)
                                ]
                                <= self.start_times_binary[
                                    (machine_idx, job_idx, time_idx)
                                ]
                            )
                            self.model += (
                                self.start_cdot_skill_level_helper_binary[
                                    (machine_idx, job_idx, time_idx, level, skill_idx)
                                ]
                                <= self.skill_level_binary[
                                    (machine_idx, time_idx, level, skill_idx)
                                ]
                            )
                            self.model += (
                                self.start_cdot_skill_level_helper_binary[
                                    (machine_idx, job_idx, time_idx, level, skill_idx)
                                ]
                                >= self.start_times_binary[
                                    (machine_idx, job_idx, time_idx)
                                ]
                                + self.skill_level_binary[
                                    (machine_idx, time_idx, level, skill_idx)
                                ]
                                - 1
                            )

    def solve(self, write_verbose_output=False):
        """Solves the model with GUROBI"""
        ######################
        # SOLVING WITH GUROBI#
        ######################

        self.model.solve(
            GUROBI(
                mip=True,
                logPath=self.RESULTS_DIR + "gurobi_log.txt",
                timeLimit=6000,
                displayInterval=5,
            )
        )
        self.lateness = self.lateness.varValue

        if write_verbose_output:
            #############################
            # EXTRACTING VARIABLE VALUES#
            #############################
            results = {}

            results["start_times_binary"] = [
                index
                for index, var in self.start_times_binary.items()
                if var.value() == 1
            ]

            results["skill_level_binary"] = [
                index
                for index, var in self.skill_level_binary.items()
                if var.value() == 1
            ]

            results["processing_times"] = {
                str(index): var.value()
                for index, var in self.processing_times_integer.items()
            }

            results["machine_one_job_constraint_helper_binary"] = [
                index
                for index, var in self.machine_one_job_constraint_helper_binary.items()
                if var.value() == 1
            ]

            results["start_cdot_duration_helper_binary"] = [
                index
                for index, var in self.start_cdot_duration_helper_binary.items()
                if var.value() == 1
            ]
            results["start_cdot_skill_level_helper_binary"] = [
                index
                for index, var in self.start_cdot_skill_level_helper_binary.items()
                if var.value() == 1
            ]

            filename = os.path.join(self.RESULTS_DIR, "variable_values_debug_1.json")
            counter = 1
            while os.path.exists(filename):
                filename = os.path.join(
                    self.RESULTS_DIR, f"variable_values_debug_{counter}.json"
                )
                counter += 1
            with open(filename, "w") as f:
                json.dump(results, f, indent=4)

            self.model.writeLP(self.RESULTS_DIR + "model.lp")
