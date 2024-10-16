from calculate_lateness import calculate_lateness

class heuristic_template():
    def __init__(self, machines, jobs_seminars, config_dict) -> None:
        self.config = config_dict
        self.N_JOBS = sum([1 for x in jobs_seminars if x["type"] == "job"])
        self.N_SEMINARS = sum([1 for x in jobs_seminars if x["type"] == "seminar"])
        self.N_MACHINES = len(machines)
        self.lateness_calculator = calculate_lateness(machines, jobs_seminars, self.config)
    
    def clean_up_solution(self, solution):
        """Not in place clean up of unncessary seminars at the end of a machine

        Args:
            solution (List of Lists): List of length self.N_MACHINES containing the job order for each machine

        Returns:
            List: Cleaned up solution
        """        
        for m_idx in range(len(solution)):
            cur = self.N_JOBS
            while cur >= self.N_JOBS and len(solution[m_idx]) > 0:
                cur = solution[m_idx].pop()
            if cur < self.N_JOBS:
                solution[m_idx].append(cur)
        # c_order = [[] for _ in solution]
        # for m_idx, m in enumerate(solution):
        #     last_job_idx = None
        #     for j_idx, j in enumerate(m):
        #         if j < self.N_JOBS:
        #             last_job_idx = j_idx
        #     c_order[m_idx] = solution[m_idx][:last_job_idx+1]
        # return c_order
