import unittest
from calculate_lateness import calculate_lateness
from full_enumeration import enumerate_all_solutions
from time import time_ns
import pyperclip, math


class TestCalculateLateness(unittest.TestCase):
    """ADD dictionary to calculate lateness instantiation

    Args:
        unittest (_type_): _description_
    """

    # def test_correct_lateness_one(self):
    #     machines = [
    #         {
    #             "name": "employee #1",
    #             "index": 0,
    #             "skills": [10 for _ in range(6)],
    #             "alpha": 1.05,
    #             "beta": 2,
    #         },
    #         {
    #             "name": "employee #2",
    #             "index": 1,
    #             "skills": [5 if i % 2 == 0 else 20 for i in range(6)],
    #             "alpha": 1.1,
    #             "beta": 0,
    #         },
    #     ]
    #     jobs_seminars = [
    #         {
    #             "skill_required": 1,
    #             "skill_level_required": 9,
    #             "base_duration": 17,
    #             "deadline": 34,
    #             "index": 0,
    #             "name": "lradqpllbc",
    #             "type": "job",
    #         },
    #         {
    #             "skill_required": 3,
    #             "skill_level_required": 43,
    #             "base_duration": 10,
    #             "deadline": 40,
    #             "index": 1,
    #             "name": "jqdoueulss",
    #             "type": "job",
    #         },
    #         {
    #             "skill_required": 0,
    #             "skill_level_required": 26,
    #             "base_duration": 22,
    #             "deadline": 72,
    #             "index": 2,
    #             "name": "hrsdcibgww",
    #             "type": "job",
    #         },
    #         {
    #             "skill_required": 2,
    #             "skill_level_required": 11,
    #             "base_duration": 22,
    #             "deadline": 100,
    #             "index": 3,
    #             "name": "bdgzldjktk",
    #             "type": "job",
    #         },
    #         {
    #             "skill_required": 5,
    #             "skill_level_required": 10,
    #             "base_duration": 17,
    #             "deadline": 66,
    #             "index": 4,
    #             "name": "oxircjfark",
    #             "type": "job",
    #         },
    #         {
    #             "skill_required": 0,
    #             "skill_level_required": 0,
    #             "base_duration": 5,
    #             "deadline": -1,
    #             "index": 5,
    #             "name": "seminar skill #0",
    #             "skill_improvement_baseline": 5,
    #             "type": "seminar",
    #         },
    #         {
    #             "skill_required": 1,
    #             "skill_level_required": 0,
    #             "base_duration": 5,
    #             "deadline": -1,
    #             "index": 6,
    #             "name": "seminar skill #1",
    #             "skill_improvement_baseline": 5,
    #             "type": "seminar",
    #         },
    #         {
    #             "skill_required": 2,
    #             "skill_level_required": 0,
    #             "base_duration": 5,
    #             "deadline": -1,
    #             "index": 7,
    #             "name": "seminar skill #2",
    #             "skill_improvement_baseline": 5,
    #             "type": "seminar",
    #         },
    #         {
    #             "skill_required": 3,
    #             "skill_level_required": 0,
    #             "base_duration": 5,
    #             "deadline": -1,
    #             "index": 8,
    #             "name": "seminar skill #3",
    #             "skill_improvement_baseline": 5,
    #             "type": "seminar",
    #         },
    #         {
    #             "skill_required": 4,
    #             "skill_level_required": 0,
    #             "base_duration": 5,
    #             "deadline": -1,
    #             "index": 9,
    #             "name": "seminar skill #4",
    #             "skill_improvement_baseline": 5,
    #             "type": "seminar",
    #         },
    #         {
    #             "skill_required": 5,
    #             "skill_level_required": 0,
    #             "base_duration": 5,
    #             "deadline": -1,
    #             "index": 10,
    #             "name": "seminar skill #5",
    #             "skill_improvement_baseline": 5,
    #             "type": "seminar",
    #         },
    #     ]
    #     calculator = calculate_lateness(machines, jobs_seminars)
    #     # Indices:
    #     # 0 to 4 are jobs
    #     # 5 to 10 are seminars
    #     order = [[2, 1, 6, 7, 3], [0, 9, 7, 4]]
    #     result = calculator.calculate(order)
    #     self.assertEqual(result, 61)


class TestFullEnumeration(unittest.TestCase):
    """SOMEHOW compare the results

    Args:
        unittest (_type_): _description_
    """

    # def test_manually_generated_validation(self):
    #     blob = enumerate_all_solutions(2, 0, 2)
    #     correct = [
    #         [[0, 1], []],
    #         [[1, 0], []],
    #         [[0], [1]],
    #         [[1], [0]],
    #         [[], [0, 1]],
    #         [[], [1, 0]],
    #     ]
    #     blob.sort()
    #     correct.sort()
    #     self.assertEqual(blob, correct)

    def calculate_expression(self, M, J, S):
        return (
            (M**J * math.factorial(J))
            * ((2**S) ** M)
            * (((J + 1) ** S) * math.factorial(S))
        )

    def test_ouput_sizes(self):
        print("Output sizes")
        output_string = []
        for job_count in range(1, 7):
            for machine_count in range(2, 3):
                for seminar_count in range(0, 4):
                    timer = time_ns()
                    length = len(
                        enumerate_all_solutions(job_count, seminar_count, machine_count)
                    )
                    upper_bound = self.calculate_expression(
                        machine_count, job_count, seminar_count
                    )
                    runtime = int((time_ns() - timer) / (10**6))
                    if runtime == 0:
                        runtime_string = "$< 1$"
                    else:
                        runtime_string = f"{runtime:,d}"
                    cur_string = f"{job_count} & {seminar_count} & {machine_count} & {length:,d} & {upper_bound:,d} & {runtime_string} \\\\"
                    output_string.append(cur_string)
                    print(cur_string)
        pyperclip.copy("\n".join(output_string))


if __name__ == "__main__":
    unittest.main()
