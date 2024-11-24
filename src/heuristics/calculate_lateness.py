from math import ceil,floor
from copy import deepcopy
import matplotlib.pyplot as plt
import time, itertools
import numpy as np


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
        self.N_JOBS = sum([1 for job in jobs_seminars if job['type'] == 'job'])
        self.debug_mode = debug_mode
        self.graph_mode = produce_graphs
        self.SKILL_LIMIT_UB = config_dict["skill_config"]["max_machine_skill"]

    def calculate(self, order, no_floats=True):
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
        lateness = None
        if self.debug_mode:
            debug_times = [[] for _ in range(len(order))]
            skill_levels = [[] for _ in range(len(order))]

        ###########
        # MACHINES#
        ###########
        # print(f"machinecount {len(current_machines)}")
        for machine_idx in range(len(current_machines)):
            current_time = 0
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
                    if not lateness or current_lateness_term > lateness:
                        lateness = current_lateness_term

                #  print(f"t {current_time} machine {machine_idx} lateness {lateness} others {current_time}+{current_processing_duration}-{current_job['deadline']}")

                else:
                    current_processing_duration = current_job["base_duration"]
                if self.debug_mode:
                    debug_times[machine_idx].append({"job": current_job['index'] , "start": current_time, "finish": current_time+current_processing_duration, "deadline": current_job['deadline']})
                    skill_levels[machine_idx].append({"time": current_time, "skills": current_machines[machine_idx]['skills']})
                current_machines[machine_idx]["skills"][
                    current_job["skill_required"]
                ] = min(
                    (
                        current_machines[machine_idx]["beta"]
                        + current_machines[machine_idx]["alpha"]
                        * current_machines[machine_idx]["skills"][
                            current_job["skill_required"]
                        ]
                    ),
                    self.SKILL_LIMIT_UB,
                )
                if no_floats:
                    current_machines[machine_idx]["skills"][
                        current_job["skill_required"]
                    ] = floor(
                        current_machines[machine_idx]["skills"][
                            current_job["skill_required"]
                        ]
                    )
                if self.debug_mode:
                    skill_levels[machine_idx].append(
                        {
                            "time": current_time+1,
                            "skills": current_machines[machine_idx]["skills"],
                        }
                    )
                current_time += current_processing_duration

        if self.debug_mode:
            # for machine in debug_times:
            #     print(machine)
            if self.graph_mode:
                self.plot_gantt_chart(debug_times)
                self.plot_skill_level_progression(skill_levels)
        return lateness

    def plot_gantt_chart(self, schedule):
        fig, ax = plt.subplots(figsize=(10, 6))

        # Loop through each machine's schedule
        for machine_id, jobs in enumerate(schedule):
            # Use alternating colors for jobs on the same machine
            machine_colors = itertools.cycle(['tab:blue', 'tab:cyan'])  # Reset colors for each machine
            for job in jobs:
                start = job["start"]
                end = job["finish"]
                job_id = job["job"]

                color = 'orange' if job_id >= self.N_JOBS else next(machine_colors)

                # Add a bar for the job with the selected color
                ax.broken_barh([(start, end - start)], (machine_id - 0.4, 0.8), facecolors=color)

                # Add job ID as label
                ax.text((start + end) / 2, machine_id, f"{job_id} ({job['deadline']})", 
                        ha='center', va='center', color='white', fontsize=10)

        # Set labels and remove grid lines
        ax.set_yticks(range(len(schedule)))
        ax.set_yticklabels([f"Machine {i+1}" for i in range(len(schedule))])
        ax.set_xlabel("Time")
        ax.set_ylabel("Machines")
        ax.set_title("Gantt Chart for Jobs")
        ax.grid(False)  # Disable grid lines
        # Set x-ticks to full integers only
        max_time = max(job["finish"] for machine in schedule for job in machine)
        ax.set_xticks(range(0, max_time + 1))  # Full integer steps

        plt.savefig(f"results/plots/{int(time.time())}_gantt.png", bbox_inches="tight")
        plt.close(fig)

    def plot_skill_level_progression(self, skill_levels):
        # X is time
        # Y is skill level
        # Each line represents another skill
        # One diagram for each machine -> In a grid so it is one picture
        # Create subplots to fit all machines in one grid layout
        num_machines = len(skill_levels)
        _, axes = plt.subplots(num_machines, 1, figsize=(10, 5 * num_machines))

        # Loop through each machine and plot its skill levels over time
        for machine_idx, machine_data in enumerate(skill_levels):
            if machine_data == []: continue
            # Extract time and skill data
            times = [entry["time"] for entry in machine_data]
            skills = np.array([entry["skills"] for entry in machine_data])
            # Plot each skill as a separate line
            ax = axes[machine_idx] if num_machines > 1 else axes  # Axes for the current machine
            for skill_idx in range(skills.shape[1]):
                skill_data = skills[:, skill_idx]
                ax.plot(times, skill_data, label=f'{self.config_dict["skills"][skill_idx]}')

                # Add circles where skill levels increase
                for i in range(1, len(skill_data)):
                    if skill_data[i] > skill_data[i - 1]:  # Check for an increase
                        ax.plot(times[i], skill_data[i], 'o', color='red')  # Plot a small red circle

            # Set labels and title
            # Set y-ticks and their range
            ax.set_yticks(
                range(1, self.config_dict["skill_config"]["max_machine_skill"] + 1)
            )
            ax.set_xlabel('Time')
            ax.set_ylabel('Skill Level')
            ax.set_title(f'Machine {machine_idx + 1}')
            ax.legend()
            ax.grid(False)

        # Adjust layout for better spacing
        plt.tight_layout()

        # Save the plot as an image
        plt.savefig(f"results/plots/{int(time.time())}_skills.png")
