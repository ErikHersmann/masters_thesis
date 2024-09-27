import json
from pulp import LpVariable, LpProblem, LpMinimize, GUROBI


RESULTS_DIR = "results/"


class linear_solver:
    def __init__(self, verbose=False) -> None:
        self.model = None
        self.runtime = None
        with open("../../resources/config.json", "r") as f:
            self.config_dict = json.load(f)
        self.verbose = verbose
        self.N_JOBS = None
        self.N_MACHINES = None
        self.N_TIME = self.config_dict["max_time"]
        self.SKILL_LEVEL_LB = self.config_dict["skill_config"]["min_machine_skill"]
        self.SKILL_LEVEL_UB = self.config_dict["skill_config"]["max_machine_skill"]
        self.SKILLS = self.config_dict["skills"]
        self.N_SKILLS = len(self.SKILLS)
        self.jobs = None
        self.seminars = None
        self.qualifications = None
        self.lateness = None
        self.BIG_M = None
        self.N_SEMINARS = None

    def skill_range(self):
        """Generate an inclusive range from the lower bound of the skill level up to the upper bound (inclusive)

        Returns:
            Range: The above described range
        """
        return range(self.SKILL_LEVEL_LB, self.SKILL_LEVEL_UB + 1)

    def setup(self):
        """Sets up jobs, seminars, qualifications, parameters by reading from "../../data_generation" directory"""
        with open("../../data_generation/output/jobset_0.json", "r") as f:
            self.jobs = json.load(f)
        # add this urself
        with open("../../data_generation/output/seminarset_basic_0.json", "r") as f:
            self.seminars = json.load(f)
        with open("../../data_generation/output/machineset_0.json", "r") as f:
            self.qualifications = json.load(f)
        with open("../../data_generation/output/learning_curveset_0.json") as f:
            learning_curves = json.load(f)
            self.learning_curves = [
                {"alpha": machine["growth_const"], "beta": machine["growth_factor"]}
                for machine in learning_curves
            ]
        self.BIG_M = sum([job["base_duration"] for job in self.jobs])

        # Calculate this from the worst skilled employee at the longest job instead
        self.BIG_P = 10000
        self.N_MACHINES = len(self.qualifications)
        self.N_JOBS = len(self.jobs)
        self.N_SEMINARS = len(self.seminars)
        self.N_JOBS_AND_SEMINARS = self.N_JOBS + self.N_SEMINARS
        print(
            f"Jobs {self.N_JOBS} Machines: {self.N_MACHINES} Skills: {self.N_SKILLS} Time: {self.N_TIME} Product {self.N_JOBS*self.N_MACHINES*self.N_TIME*self.N_SKILLS}"
        )

    def compile(self):
        """Instantiates model"""
        self.model = LpProblem("Open_Shop", LpMinimize)

        ############
        # VARIABLES#
        ############
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
        # Not sure if this is a decision variable
        self.processing_times = LpVariable.dicts(
            "d",
            [
                (machine, job, time)
                for machine in range(self.N_MACHINES)
                for job in range(self.N_JOBS)
                for time in range(self.N_TIME)
            ],
            cat="Integer",
        )
        self.start_cdot_processing_helper_binary = LpVariable.dicts(
            "b",
            [
                (machine, job, time)
                for machine in range(self.N_MACHINES)
                for job in range(self.N_JOBS)
                for time in range(self.N_TIME)
            ],
            cat="Integer",
        )
        self.machine_one_job_constraint_helper_binary = LpVariable.dicts(
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
        self.lateness = LpVariable("lateness", lowBound=0, cat="Integer")
        for job in range(self.N_JOBS):
            for machine in range(self.N_MACHINES):
                # sum this over t
                time_over_deadline = sum(
                    [
                        time * self.start_times_binary[(machine, job, time)]
                        + self.processing_times[(machine, job, time)]
                        - self.jobs[job]["deadline"]
                        for time in range(self.N_TIME)
                    ]
                )
                self.model += self.lateness >= time_over_deadline
        self.model += self.lateness

        ############
        # FUNCTIONS#
        ############

        # Learning curve helper function

        def learning_curve_function(machine, time, skill):
            left_side = sum(
                [
                    self.start_times_binary[(machine, job_index, time)]
                    * (
                        self.learning_curves[machine]["beta"]
                        + self.learning_curves[machine]["alpha"]
                        * sum(
                            [
                                level
                                * self.skill_level_binary[
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
                    for job_index in range(self.N_JOBS)
                ]
            )
            right_side = sum(
                [
                    level * self.skill_level_binary[(machine, time, level, skill)]
                    for level in self.skill_range()
                ]
            )
            return max(min(left_side, self.SKILL_LEVEL_UB), right_side)
            # Helper Integer here that has to be bigger than right_side and bigger than left_side
            # Return the Integer

        ##############
        # CONSTRAINTS#
        ##############

        # Set qualifications in each skill at time 0 from

        # Machines must have at most one job on them for any given time t (Currently the implementation for chapter 3.1.2 -> Update to 3.1.3)

        for job1 in range(self.N_JOBS):
            for job2 in range(job1, self.N_JOBS):
                for machine in range(self.N_MACHINES):
                    left_side = sum(
                        [
                            self.start_times_binary[(machine, job1, time)] * time
                            + self.start_cdot_processing_helper_binary[
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
                        - self.BIG_M
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
                            + self.start_cdot_processing_helper_binary[
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
                        - self.BIG_M
                        * self.machine_one_job_constraint_helper_binary[
                            (job1, job2, machine)
                        ]
                        <= right_side_alt
                    )

        # Helper variable that models the multiplication constraints

        for machine in range(self.N_MACHINES):
            for job in range(self.N_JOBS):
                for time in range(self.N_TIME):
                    self.model += (
                        self.start_cdot_processing_helper_binary[(machine, job, time)]
                        <= self.start_times_binary[(machine, job, time)] * self.BIG_P
                    )
                    self.model += (
                        self.start_cdot_processing_helper_binary[(machine, job, time)]
                        >= 0
                    )
                    self.model += (
                        self.start_cdot_processing_helper_binary[(machine, job, time)]
                        <= self.processing_times[(machine, job, time)]
                    )
                    self.model += (
                        self.start_cdot_processing_helper_binary[(machine, job, time)]
                        >= self.processing_times[(machine, job, time)]
                        - (1 - self.start_times_binary[(machine, job, time)])
                        * self.BIG_P
                    )

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
            for seminar in range(self.N_SEMINARS):
                self.model += (
                    sum(
                        [
                            self.start_times_binary[
                                (machine, self.N_JOBS + seminar, time)
                            ]
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
                    self.model += self.processing_times[
                        (machine, job_index, time)
                    ] == sum(
                        [
                            sum(
                                [
                                    self.skill_level_binary[
                                        (machine, time, level, skill)
                                    ]
                                    * (
                                        (
                                            current_job["skill_level_required"]
                                            * current_job["base_duration"]
                                        )
                                        / level
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
                            self.skill_level_binary[
                                (
                                    machine,
                                    time + 1,
                                    learning_curve_function(machine, time, skill),
                                    skill,
                                )
                            ]
                            == 1
                        )

        # Skill level increase only constraint

        for machine in range(self.N_MACHINES):
            for time in range(1, self.N_TIME):
                for skill in range(self.N_SKILLS):
                    left_side = sum(
                        [
                            level
                            * self.skill_level_binary[(machine, time, level, skill)]
                            for level in self.skill_range()
                        ]
                    )
                    right_side = sum(
                        [
                            level
                            * self.skill_level_binary[(machine, time - 1, level, skill)]
                            for level in self.skill_range()
                        ]
                    )
                    self.model += left_side >= right_side

        # Skill level at start constraint

        for machine in range(self.N_MACHINES):
            for skill in range(self.N_SKILLS):
                self.model += (
                    self.skill_level_binary[
                        (
                            machine,
                            0,
                            self.qualifications[machine]["skills"][skill],
                            skill,
                        )
                    ]
                    == 1
                )

        # An employee should always only possess one level for a given skill

        for machine in range(self.N_MACHINES):
            for skill in range(self.N_SKILLS):
                for time in range(self.N_TIME):
                    self.model += (
                        sum(
                            [
                                self.skill_level_binary[
                                    (
                                        machine,
                                        time,
                                        level,
                                        skill,
                                    )
                                ]
                                for level in self.skill_range()
                            ]
                        )
                    ) == 1

    def solve(self):
        """Solves the model with GUROBI"""
        ######################
        # SOLVING WITH GUROBI#
        ######################

        self.model.solve(
            GUROBI(
                mip=True,
                logPath=RESULTS_DIR + "gurobi_log.txt",
                timeLimit=30,
                displayInterval=5,
            )
        )
        self.lateness = self.lateness.varValue

        #############################
        # EXTRACTING VARIABLE VALUES#
        #############################

        results = {}

        results["start_times_binary"] = [
            index for index, var in self.start_times_binary.items() if var.value() == 1
        ]

        results["skill_level_binary"] = [
            index for index, var in self.skill_level_binary.items() if var.value() == 1
        ]

        results["processing_times"] = {
            str(index): var.value() for index, var in self.processing_times.items()
        }

        results["machine_one_job_constraint_helper_binary"] = [
            index
            for index, var in self.machine_one_job_constraint_helper_binary.items()
            if var.value() == 1
        ]

        with open(RESULTS_DIR + "variable_values_debug.json", "w") as f:
            json.dump(results, f, indent=4)


if __name__ == "__main__":
    solver = linear_solver(verbose=True)
    solver.setup()
    solver.compile()
    solver.solve()
