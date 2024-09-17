# Notes
## Notes from first meeting
- How is a solution being encoded (Vector of jobs for each machine (the order))
	- Issues with that: Calculate objective function value from a solution is "non-trivial"
- Linearize model: use the binary decision variable with the following 5 indices: (job, )machine, time, competence-index, competence-level (to solve via a MIP model)
- Get an upper bound from heuristics or construct one from a feasible solution for T and competence-levels
- Reasoning for generation of data from company data or random sampling (based on company data)
- don't use stochastic functions as learning effect functions (put that in the "directions for future research" part)
- use a greedy heuristic and improve upon that via neighborhood-search (should have been done already in the literature for similar problems)

## To do 
1. Grab the WLS license for gurobi on laptop (copy the file or something ?)
1. linearize problem  
	1. MIP Solver (Gurobi)
1. construct own heuristic (with literature help)
1. Compare/Generate results and send supervisor an email
2. Work on data generation (random and company)
1. Generate problem specific instance (with real world values from company data)
