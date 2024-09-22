import json
from math import ceil


class heuristic_1:
    def __init__(self, verbose=False) -> None:
        ########
        # SETUP#
        ########
        self.verbose = verbose
        with open("../../resources/config.json", "r") as f:
            self.config_dict = json.load(f)

        self.number_of_machines = self.config_dict["number_of_machines"]
        # must be a list of dicts
        self.job_order_on_machines = [[] for _ in range(self.number_of_machines)]

        # this should come from a file or generator function and contain tuples like this
        # single_job = {'skill_required': Skills.C_Sharp,
        #               'skill_level_required': 5,
        #               'base_duration': 20,
        #               'deadline': 40,
        #               'index': 0,
        #               'name': "performance benchmarking",
        #              }
        with open("../../data_generation/output/jobset_0.json", "r") as f:
            self.jobs = json.load(f)
        # add this urself
        with open("../../data_generation/output/seminarset_basic_0.json", "r") as f:
            self.seminars = json.load(f)
        with open("../../data_generation/output/machineset_0.json", "r") as f:
            self.machine_qualifications = json.load(f)
        with open("../../data_generation/output/learning_curveset_0.json") as f:
            learning_curves = json.load(f)
            self.learning_curves = [
                lambda skill_level: int(skill_level * machine["growth_factor"])
                + machine["growth_const"]
                for machine in learning_curves
            ]

        if self.verbose:
            self.dprint(self.jobs, "Jobs")
            self.dprint(self.seminars, "Seminars")
            self.dprint(self.machine_qualifications, "Machines")

    def dprint(self, dictionary_list, name):
        """Helper function to pretty print the list of dictionaries

        Args:
            dictionary_list (list of dictionaries): A list of dictionaries (of similar or same structure)
            name (String): Name of the dictionar structure (for printing)
        """
        print(f"{name}\n")
        for row in dictionary_list:
            print(row)
        print()

    def sort_jobs_by_priority(self, jobs_list, mode=0):
        """Sorts the available jobs according to a rule specified in mode

        Args:
            jobs_list (List of dictionaries): A list of dictionaries (of the job structure) refer to the generator scripts for a sample
            mode (int, optional): A mode that specifies the rule according to which the jobs are supposed to be sorted. Defaults to 0.

        Returns:
            List of dictionaries: Returns the jobs_list sorted according to the specified mode
        """
        match mode:
            case 0:
                return enumerate(jobs_list)
            case 1:
                return sorted(enumerate(jobs_list), key=lambda x: x[1]["deadline"])

    def calculate_lateness(self):
        lateness = 0
        for machine in self.job_order_on_machines:
            for job in machine:
                lateness += job["end_time"] - job["deadline"]
        return lateness

    def greedy_job_assignment(self):
        if self.verbose:
            print(
                f"current machine processing time {self.all_current_machine_processing_times}\n"
            )
        machines_used_in_this_iteration = []
        for job_index, job in self.sort_jobs_by_priority(self.jobs, 1):
            # find the machine that has the shortest processing time for the current job
            if len(machines_used_in_this_iteration) == len(
                self.all_current_machine_processing_times
            ):
                break
            best_machine_idx = sorted(
                [
                    machine
                    for machine in self.all_current_machine_processing_times
                    if machine[0] not in machines_used_in_this_iteration
                ],
                key=lambda x: x[1][job_index],
                reverse=True,
            )[-1][0]
            # plan the job on that machine and dont consider it for the next few jobs
            self.job_order_on_machines[best_machine_idx].append(job)
            self.job_order_on_machines[best_machine_idx][-1][
                "start_time"
            ] = self.current_time
            self.job_order_on_machines[best_machine_idx][-1]["end_time"] = (
                self.current_time
                + [
                    processing_time
                    for processing_time in self.all_current_machine_processing_times
                    if processing_time[0] == best_machine_idx
                ][0][1][job_index]
            )
            ####################
            # update the skills#
            ####################
            skill_idx = job["skill_required"]
            current_skill_level = self.machine_qualifications[best_machine_idx][
                "skills"
            ][skill_idx]
            # processing_duration = (
            #     job_order_on_machines[best_machine_idx][-1]["end_time"]
            #     - job_order_on_machines[best_machine_idx][-1]["start_time"]
            # )

            self.machine_qualifications[best_machine_idx]["skills"][
                skill_idx
            ] = self.learning_curves[best_machine_idx](
                current_skill_level
            )  # , processing_duration

            self.jobs.remove(job)
            machines_used_in_this_iteration.append(best_machine_idx)
            # break

    def get_current_machine_processing_times(self):
        all_current_machine_processing_times = []
        # Get the last job on all machines whose finish time (on that job) is less than the current time
        currently_free_machines = [
            idx
            for idx, machine in enumerate(self.job_order_on_machines)
            if len(machine) == 0 or machine[-1]["end_time"] < self.current_time
        ]
        if self.verbose:
            print(f"t={self.current_time}\tFree machines\t{currently_free_machines}\n")
        # Before Seminars
        for machine in currently_free_machines:
            current_machine_processing_times = []
            for job in self.jobs:
                # Calculate the new processing time (Maybe use a function here to allow for changing this later however this shouldn't be too much of an issue 問題ない)
                current_machine_processing_times.append(
                    ceil(
                        job["base_duration"]
                        * (
                            job["skill_level_required"]
                            / self.machine_qualifications[machine]["skills"][
                                job["skill_required"]
                            ]
                        )
                    )
                )
            all_current_machine_processing_times.append(
                (machine, current_machine_processing_times)
            )
        return all_current_machine_processing_times

    def calculate_lateness_next_step(self):
        return 0

    def optimize(self):
        """Main loop to optimize the schedule on the given dataset"""
        self.current_time = 0
        while len(self.jobs) > 0:
            if self.verbose:
                print(f"t\t{self.current_time}")
            self.dprint(self.machine_qualifications, "Qualifications")
            # Calculate times list for all jobs for all free machines
            self.all_current_machine_processing_times = (
                self.get_current_machine_processing_times()
            )

            # maybe instead consider for each singular job which an employee would get due to the priority ranking if a seminar at the start would reduce the end_time just for that job and if so:
            # plan a seminar

            # Calculate the lateness of the jobs in the next step
            pre_seminar_lateness = self.calculate_lateness_next_step()
            # Recalculate with seminars
            post_seminar_lateness = self.calculate_lateness_next_step()

            if post_seminar_lateness < pre_seminar_lateness:
                pass

            # Greedily pick the earliest deadline jobs and the fastest worker on them ?
            self.greedy_job_assignment()

            if self.verbose:
                self.dprint(self.job_order_on_machines, "Order")
            self.current_time = (
                min(
                    [
                        job_on_machine[-1]["end_time"]
                        for job_on_machine in self.job_order_on_machines
                    ]
                )
                + 1
            )

        ##########
        # RESULTS#
        ##########

        print(self.calculate_lateness())


if __name__ == "__main__":
    heuristic = heuristic_1(True)
    heuristic.optimize()
