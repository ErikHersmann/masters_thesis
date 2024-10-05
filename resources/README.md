# Notes
## Notes from first meeting
- How is a solution being encoded (Vector of jobs for each machine (the order))
	- Issues with that: Calculate objective function value from a solution is "non-trivial"
- Linearize model: use the binary decision variable with the following 5 indices: (job, )machine, time, competence-index, competence-level (to solve via a MIP model)
- Get an upper bound from heuristics or construct one from a feasible solution for T and competence-levels
- Reasoning for generation of data from company data or random sampling (based on company data)
- don't use stochastic functions as learning effect functions (put that in the "directions for future research" part)
- use a greedy heuristic and improve upon that via neighborhood-search (should have been done already in the literature for similar problems)

## Answers regarding the first meeting
- Vector of (job/seminar indices) for each machine
- Linearization in progress
- Upper bound from heuristic (or consider no learning effect, no seminars and somehow calculate lateness from that cheaply)
- Data generation completely random for now (reason this later)
- Done
- Open (heuristic from literature)

