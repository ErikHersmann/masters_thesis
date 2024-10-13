from math import ceil
from copy import deepcopy


class calculate_lateness:
    def __init__(self, machines, jobs_seminars, config_dict, debug_mode=False) -> None:
        self.machines = machines
        self.jobs_seminars = jobs_seminars
        self.debug_mode = debug_mode
        self.SKILL_LIMIT_UB = config_dict["skill_config"]["max_machine_skill"]

    def calculate(self, order):
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
                    debug_times[machine_idx].append({"job": current_job['index'] , "start": current_time, "finish": current_time+current_processing_duration})
                current_machines[machine_idx]["skills"][current_job["skill_required"]] = min(
                    (
                        current_machines[machine_idx]["beta"]
                        + current_machines[machine_idx]["alpha"]
                        * current_machines[machine_idx]["skills"][current_job["skill_required"]]
                    ),
                    self.SKILL_LIMIT_UB,
                )
                current_time += current_processing_duration
        if self.debug_mode:
            for machine in debug_times:
                print(machine)
        return lateness



