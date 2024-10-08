import unittest
from calculate_lateness import calculate_lateness


class TestCalculateLateness(unittest.TestCase):

    def test_correct_lateness_one(self):
        machines = [
            {
                "name": "employee #1",
                "index": 0,
                "skills": [10 for _ in range(6)],
                "alpha": 1.05,
                "beta": 2,
            },
            {
                "name": "employee #2",
                "index": 1,
                "skills": [5 if i % 2 == 0 else 20 for i in range(6)],
                "alpha": 1.1,
                "beta": 0,
            },
        ]
        jobs_seminars = [
            {
                "skill_required": 1,
                "skill_level_required": 9,
                "base_duration": 17,
                "deadline": 34,
                "index": 0,
                "name": "lradqpllbc",
                "type": "job",
            },
            {
                "skill_required": 3,
                "skill_level_required": 43,
                "base_duration": 10,
                "deadline": 40,
                "index": 1,
                "name": "jqdoueulss",
                "type": "job",
            },
            {
                "skill_required": 0,
                "skill_level_required": 26,
                "base_duration": 22,
                "deadline": 72,
                "index": 2,
                "name": "hrsdcibgww",
                "type": "job",
            },
            {
                "skill_required": 2,
                "skill_level_required": 11,
                "base_duration": 22,
                "deadline": 100,
                "index": 3,
                "name": "bdgzldjktk",
                "type": "job",
            },
            {
                "skill_required": 5,
                "skill_level_required": 10,
                "base_duration": 17,
                "deadline": 66,
                "index": 4,
                "name": "oxircjfark",
                "type": "job",
            },
            {
                "skill_required": 0,
                "skill_level_required": 0,
                "base_duration": 5,
                "deadline": -1,
                "index": 5,
                "name": "seminar skill #0",
                "skill_improvement_baseline": 5,
                "type": "seminar",
            },
            {
                "skill_required": 1,
                "skill_level_required": 0,
                "base_duration": 5,
                "deadline": -1,
                "index": 6,
                "name": "seminar skill #1",
                "skill_improvement_baseline": 5,
                "type": "seminar",
            },
            {
                "skill_required": 2,
                "skill_level_required": 0,
                "base_duration": 5,
                "deadline": -1,
                "index": 7,
                "name": "seminar skill #2",
                "skill_improvement_baseline": 5,
                "type": "seminar",
            },
            {
                "skill_required": 3,
                "skill_level_required": 0,
                "base_duration": 5,
                "deadline": -1,
                "index": 8,
                "name": "seminar skill #3",
                "skill_improvement_baseline": 5,
                "type": "seminar",
            },
            {
                "skill_required": 4,
                "skill_level_required": 0,
                "base_duration": 5,
                "deadline": -1,
                "index": 9,
                "name": "seminar skill #4",
                "skill_improvement_baseline": 5,
                "type": "seminar",
            },
            {
                "skill_required": 5,
                "skill_level_required": 0,
                "base_duration": 5,
                "deadline": -1,
                "index": 10,
                "name": "seminar skill #5",
                "skill_improvement_baseline": 5,
                "type": "seminar",
            },
        ]
        calculator = calculate_lateness(machines, jobs_seminars)
        # Indices:
        # 0 to 4 are jobs
        # 5 to 10 are seminars
        order = [[2, 1, 6, 7, 3], [0, 9, 7, 4]]
        result = calculator.calculate(order)
        self.assertEqual(result, 13)


if __name__ == "__main__":
    unittest.main()
