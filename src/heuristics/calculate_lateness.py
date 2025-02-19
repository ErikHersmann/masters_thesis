from math import ceil, floor
from copy import deepcopy
import matplotlib.pyplot as plt
import time, itertools
import numpy as np
from functools import cache


class calculate_lateness:

    def __init__(
        self,
        machines,
        jobs_seminars,
        config_dict,
        debug_mode=False,
        produce_graphs=False,
    ) -> None:
        self.config_dict = config_dict
        self.machines = machines
        self.jobs_seminars = jobs_seminars
        self.N_JOBS = sum([1 for job in jobs_seminars if job["type"] == "job"])
        self.debug_mode = debug_mode
        self.graph_mode = produce_graphs
        self.SKILL_LIMIT_UB = config_dict["skill_config"]["max_machine_skill"]

    def calculate(self, order, no_floats=True):
        return self._calculate(tuple([tuple(x) for x in order]), no_floats=no_floats)

    @cache
    def _calculate(self, order, no_floats=True):
        """Given a List of Lists of orders of jobs (with details of each job/seminar), and the machines at t=0
        Calculate the lateness of the given solution (order vectors)

        Args:
            order_on_machines (List of List of int): A list of length N_MACHINES that contains indices that point to jobs or seminars
            machines (List of Dicts with Machine structure): List of machine qualifications and learning curve parameters

        Returns:
            int: The lateness of the given solution
        """
        order = [[self.jobs_seminars[idx] for idx in machine] for machine in order]
        current_machines = deepcopy(self.machines)
        lateness = []
        if self.debug_mode:
            debug_times = [[] for _ in range(len(order))]
            skill_levels = [[] for _ in range(len(order))]

        ###########
        # MACHINES#
        ###########
        # print(f"machinecount {len(current_machines)}")
        for machine_idx in range(len(current_machines)):
            current_time = 0
            if self.debug_mode:
                skill_levels[machine_idx].append(
                    {
                        "time": 0,
                        "skills": deepcopy(current_machines[machine_idx]["skills"]),
                    }
                )
            #######
            # JOBS#
            #######
            while len(order[machine_idx]) > 0:
                current_job = order[machine_idx].pop(0)
                if current_job["type"] != "seminar":
                    current_processing_duration = ceil(
                        current_job["base_duration"]
                        * (
                            current_job["skill_level_required"]
                            / current_machines[machine_idx]["skills"][
                                current_job["skill_required"]
                            ]
                        )
                    )
                    current_lateness_term = (
                        current_time
                        + current_processing_duration
                        - current_job["deadline"]
                    )
                    lateness.append(current_lateness_term)

                    # print(f"t {current_time} machine {machine_idx} lateness {max(lateness)} others {current_time}+{current_processing_duration}-{current_job['deadline']}")

                else:
                    current_processing_duration = current_job["base_duration"]
                if self.debug_mode:
                    debug_times[machine_idx].append(
                        {
                            "job": current_job["index"],
                            "start": current_time,
                            "finish": current_time + current_processing_duration,
                            "deadline": current_job["deadline"],
                        }
                    )

                ###################
                # UPDATING SKILLS #
                ###################

                new_skill_level = min(
                    current_machines[machine_idx]["skills"][
                        current_job["skill_required"]
                    ]
                    + (
                        current_machines[machine_idx]["alpha"]
                        * (
                            (
                                self.SKILL_LIMIT_UB
                                - current_machines[machine_idx]["skills"][
                                    current_job["skill_required"]
                                ]
                            )
                            / self.SKILL_LIMIT_UB
                        )
                    ),
                    self.SKILL_LIMIT_UB,
                )
                # print(
                #     current_machines[machine_idx]["skills"][
                #         current_job["skill_required"]
                #     ], new_skill_level
                # )
                current_machines[machine_idx]["skills"][
                    current_job["skill_required"]
                ] = new_skill_level
                if no_floats:
                    current_machines[machine_idx]["skills"][
                        current_job["skill_required"]
                    ] = floor(
                        current_machines[machine_idx]["skills"][
                            current_job["skill_required"]
                        ]
                    )
                current_time += current_processing_duration
            if self.debug_mode:
                skill_levels[machine_idx].append(
                    {
                        "time": -1,
                        "skills": current_machines[machine_idx]["skills"],
                    }
                )

        if self.debug_mode:
            # for machine in debug_times:
            #     print(machine)
            if self.graph_mode:
                self.plot_gantt_chart(debug_times)
                self.plot_skill_level_progression(skill_levels)
        return max(lateness)

    def plot_gantt_chart(self, schedule):
        fig, ax = plt.subplots(figsize=(15, 6))

        for machine_id, jobs in enumerate(schedule):
            machine_colors = itertools.cycle(["tab:blue", "tab:cyan"])
            for job in jobs:
                start = job["start"]
                end = job["finish"]
                job_id = job["job"]

                color = "orange" if job_id >= self.N_JOBS else next(machine_colors)

                ax.broken_barh(
                    [(start, end - start)], (machine_id - 0.4, 0.8), facecolors=color
                )

                ax.text(
                    (start + end) / 2,
                    machine_id,
                    f"{job_id} ({job['deadline']})",
                    ha="center",
                    va="center",
                    color="white",
                    fontsize=10,
                )

        ax.set_yticks(range(len(schedule)))
        ax.set_yticklabels([f"Machine {i+1}" for i in range(len(schedule))])
        ax.set_xlabel("Time")
        ax.set_ylabel("Machines")
        ax.set_title("Gantt Chart for Jobs")
        ax.grid(False)
        max_time = max(job["finish"] for machine in schedule for job in machine)
        ax.set_xticks(range(0, max_time + 1, 5))  # Full integer steps

        plt.savefig(f"results/plots/{int(time.time())}_gantt.png", bbox_inches="tight")
        plt.close(fig)

    def plot_skill_level_progression(self, skill_levels):
        skill_names = self.config_dict["skills"]
        num_skills = len(skill_names)
        machine_colors = plt.cm.get_cmap("tab10", len(skill_levels))
        initial_levels = []
        final_levels = []

        for _, machine_data in enumerate(skill_levels):
            if not machine_data:
                continue

            initial_skills = machine_data[0]["skills"]
            final_skills = machine_data[-1]["skills"]

            initial_levels.append(initial_skills)
            final_levels.append(final_skills)

        _, axes = plt.subplots(2, 1, figsize=(12, 9))
        x = np.arange(num_skills)
        bar_width = 0.8 / len(initial_levels)

        for idx, levels in enumerate(initial_levels):
            bars = axes[0].bar(
                x + idx * bar_width,
                levels,
                bar_width,
                label=f"Machine {idx}",
                color=machine_colors(idx),
            )
            axes[0].bar_label(bars, fmt="%d", label_type="center", rotation=90)

        axes[0].set_title("Initial Skill Levels (Before the first job)")
        axes[0].set_ylabel("Skill Level")
        axes[0].set_xticks(x + (bar_width * len(initial_levels)) / 2)
        axes[0].set_xticklabels(skill_names, rotation=90)
        axes[0].legend()

        for idx, levels in enumerate(final_levels):
            bars = axes[1].bar(
                x + idx * bar_width,
                levels,
                bar_width,
                label=f"Machine {idx}",
                color=machine_colors(idx),
            )
            axes[1].bar_label(bars, fmt="%d", label_type="center", rotation=90)

        axes[1].set_title("Final Skill Levels (After the last job)")
        axes[1].set_ylabel("Skill Level")
        axes[1].set_xticks(x + (bar_width * len(final_levels)) / 2)
        axes[1].set_xticklabels(skill_names, rotation=90)
        axes[1].legend()

        plt.tight_layout()
        timestamp = int(time.time())
        plt.savefig(f"results/plots/{timestamp}_skills.png")
