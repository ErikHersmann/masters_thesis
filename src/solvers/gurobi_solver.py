import json, os
from pulp import LpVariable, LpProblem, LpMinimize, GUROBI
from math import ceil


class linear_solver:

    def __init__(self, machines, jobs_seminars, config_dict, verbose=False) -> None:
        self.RESULTS_DIR = "results/"
        self.config_dict = config_dict
        self.verbose = verbose
        self.SKILL_LEVEL_LB = self.config_dict["skill_config"]["min_machine_skill"]
        self.SKILL_LEVEL_UB = self.config_dict["skill_config"]["max_machine_skill"]
        self.SKILLS = self.config_dict["skills"]
        self.N_SKILLS = len(self.SKILLS)
        self.ALMOST_ONE = 0.999999
        self.machines = machines
        self.jobs_seminars = jobs_seminars
        worst_skills = [
            min([machine["skills"][skill_idx] for machine in self.machines])
            for skill_idx in range(self.N_SKILLS)
        ]
        worst_processing_times = [
            (
                (job["base_duration"] * job["skill_level_required"])
                / worst_skills[job["skill_required"]]
                if job["type"] == "job"
                else job["base_duration"]
            )
            for job in self.jobs_seminars
        ]
        self.BIG_M_XOR = ceil(sum(worst_processing_times)) + 1
        self.BIG_M_CAP = ceil(max(worst_processing_times)) + 1
        self.BIG_M_MAX = self.SKILL_LEVEL_UB + 1
        self.N_MACHINES = len(self.machines)
        self.N_JOBS = sum([1 for x in self.jobs_seminars if x["type"] == "job"])
        self.N_SEMINARS = sum([1 for x in self.jobs_seminars if x["type"] == "seminar"])
        self.N_JOBS_AND_SEMINARS = len(self.jobs_seminars)
        self.N_TIME = self.BIG_M_XOR
        if self.verbose:
            print(
                f"Jobs {self.N_JOBS} Seminars {self.N_SEMINARS} Machines {self.N_MACHINES} Skills {self.N_SKILLS} Time {self.N_TIME} Level {self.SKILL_LEVEL_UB-self.SKILL_LEVEL_LB} Product {self.N_JOBS_AND_SEMINARS*self.N_MACHINES*self.N_TIME*self.N_SKILLS*(self.SKILL_LEVEL_UB-self.SKILL_LEVEL_LB)}"
            )

    def skill_range(self):
        """Generate an inclusive range from the lower bound of the skill level up to the upper bound (inclusive)

        Returns:
            Range: The above described range
        """
        return range(self.SKILL_LEVEL_LB, self.SKILL_LEVEL_UB + 1)

    def pre_compile(self):
        """Instantiates the model instance and the variables"""
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
                if job1 != job2
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
            cat="Integer",
            lowBound=0,
            upBound=self.BIG_M_CAP,
        )
        self.skill_increased_helper_binary = LpVariable.dicts(
            "d",
            [
                (machine, time, skill)
                for machine in range(self.N_MACHINES)
                for time in range(self.N_TIME - 1)
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
                for time in range(self.N_TIME - 1)
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
            lowBound=1,
            upBound=self.BIG_M_CAP,
        )
        print(f"proctime lower bound 1\nproctime upper bound {self.BIG_M_CAP}")
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
        print(
            f"lateness lower bound {lb_lateness}\nlateness upper bound {self.BIG_M_XOR+1}"
        )
        self.lateness = LpVariable(
            "lateness",
            lowBound=lb_lateness,
            upBound=self.BIG_M_XOR,
            cat="Integer",
        )
        for job in range(self.N_JOBS):
            time_over_deadline = sum(
                [
                    time * self.start_times_binary[(machine, job, time)]
                    + self.start_cdot_duration_helper_binary[(machine, job, time)]
                    - (
                        self.jobs_seminars[job]["deadline"]
                        * self.start_times_binary[(machine, job, time)]
                    )
                    for time in range(self.N_TIME)
                    for machine in range(self.N_MACHINES)
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

        # Helper variable that models the multiplication constraints

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
                    self.model += (
                        self.start_cdot_duration_helper_binary[(machine, job, time)]
                        <= self.processing_times_integer[(machine, job, time)]
                    )
                    self.model += (
                        self.start_cdot_duration_helper_binary[(machine, job, time)]
                        >= self.processing_times_integer[(machine, job, time)]
                        - (1 - self.start_times_binary[(machine, job, time)])
                        * self.BIG_M_CAP
                    )

        # Calculate processing durations

        for job_index in range(self.N_JOBS):
            current_job = self.jobs_seminars[job_index]
            current_job_term = (
                current_job["skill_level_required"] * current_job["base_duration"]
            )
            for machine in range(self.N_MACHINES):
                for time in range(self.N_TIME):  # -1
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

        # Skill level at start constraint

        for machine_idx in range(self.N_MACHINES):
            for skill_idx in range(self.N_SKILLS):
                self.model += (
                    self.skill_level_binary[
                        (
                            machine_idx,
                            0,
                            self.machines[machine_idx]["skills"][skill_idx],
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

        #######################################
        # CONSTRAINTS FOR SKILL LEVEL UPDATING#
        #######################################

        for machine_idx in range(self.N_MACHINES):
            alpha = self.machines[machine_idx]["alpha"]
            beta = self.machines[machine_idx]["beta"]
            l_cap = self.machines[machine_idx]["l_cap"]
            for time_idx in range(self.N_TIME - 1):
                for skill_idx in range(self.N_SKILLS):
                    new_level_or_zero = sum(
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
                    left_side = sum(
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
                    # should be bigger or equal the new level or 0
                    self.model += left_side >= new_level_or_zero - self.ALMOST_ONE
                    # should always be bigger or equal the old level
                    self.model += left_side >= old_level
                    # should be smaller or equal to the new level if d = 0
                    self.model += (
                        left_side
                        <= self.BIG_M_MAX
                        * self.skill_increased_helper_binary[
                            (machine_idx, time_idx, skill_idx)
                        ]
                        + new_level_or_zero
                    )
                    # should be smaller or equal to the old level if d = 1
                    self.model += (
                        left_side
                        <= self.BIG_M_MAX
                        * (
                            1
                            - self.skill_increased_helper_binary[
                                (machine_idx, time_idx, skill_idx)
                            ]
                        )
                        + old_level
                    )

        # Constraints for multiplication helper variable

        for machine_idx in range(self.N_MACHINES):
            for job_idx in range(self.N_JOBS_AND_SEMINARS):
                for time_idx in range(self.N_TIME - 1):
                    self.model += (
                        sum(
                            [
                                self.start_cdot_skill_level_helper_binary[
                                    (
                                        machine_idx,
                                        job_idx,
                                        time_idx,
                                        level_temp,
                                        self.jobs_seminars[job_idx]["skill_required"],
                                    )
                                ]
                                for level_temp in self.skill_range()
                            ]
                        )
                        <= self.start_times_binary[(machine_idx, job_idx, time_idx)]
                    )
                    self.model += (
                        sum(
                            [
                                self.start_cdot_skill_level_helper_binary[
                                    (
                                        machine_idx,
                                        job_idx,
                                        time_idx,
                                        level_temp,
                                        skill_idx_temp,
                                    )
                                ]
                                for level_temp in self.skill_range()
                                for skill_idx_temp in range(self.N_SKILLS)
                            ]
                        )
                        <= self.start_times_binary[(machine_idx, job_idx, time_idx)]
                    )
                    for level in self.skill_range():
                        self.model += (
                            self.start_cdot_skill_level_helper_binary[
                                (
                                    machine_idx,
                                    job_idx,
                                    time_idx,
                                    level,
                                    self.jobs_seminars[job_idx]["skill_required"],
                                )
                            ]
                            <= self.skill_level_binary[
                                (
                                    machine_idx,
                                    time_idx,
                                    level,
                                    self.jobs_seminars[job_idx]["skill_required"],
                                )
                            ]
                        )
                        self.model += (
                            self.start_cdot_skill_level_helper_binary[
                                (
                                    machine_idx,
                                    job_idx,
                                    time_idx,
                                    level,
                                    self.jobs_seminars[job_idx]["skill_required"],
                                )
                            ]
                            >= self.start_times_binary[(machine_idx, job_idx, time_idx)]
                            + self.skill_level_binary[
                                (
                                    machine_idx,
                                    time_idx,
                                    level,
                                    self.jobs_seminars[job_idx]["skill_required"],
                                )
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

            results["skill_level_binary_m_j_t"] = {}
            for (machine, time, level, skill), var in self.skill_level_binary.items():
                if var.value() == 1:
                    time = f"t_{time}"
                    machine = f"m_{machine}"
                    if time not in results["skill_level_binary_m_j_t"]:
                        results["skill_level_binary_m_j_t"][time] = {}
                    if machine not in results["skill_level_binary_m_j_t"][time]:
                        results["skill_level_binary_m_j_t"][time][machine] = [
                            0 for _ in range(self.N_SKILLS)
                        ]
                    results["skill_level_binary_m_j_t"][time][machine][skill] = level

            results["processing_times_m_j_t"] = {
                str(index): var.value()
                for index, var in self.processing_times_integer.items()
            }

            results["machine_one_job_constraint_helper_binary"] = {
                str(index): (
                    f"m_{index[2]}    j_{index[0]} -> j_{index[1]}"
                    if var.value() == 1
                    else f"m_{index[2]}    j_{index[1]} -> j_{index[0]}"
                )
                for index, var in self.machine_one_job_constraint_helper_binary.items()
            }

            results["start_cdot_duration_helper_binary"] = {
                str(index): var.value()
                for index, var in self.start_cdot_duration_helper_binary.items()
                if var.value() != 0
            }
            results["start_cdot_skill_level_helper_binary"] = [
                index
                for index, var in self.start_cdot_skill_level_helper_binary.items()
                if var.value() == 1
            ]
            results["machines"] = self.machines
            results["jobs_seminars"] = self.jobs_seminars

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
