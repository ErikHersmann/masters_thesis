# Notes (Alt key for menu bar)
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

## Questions for meeting 2
- variable naming conventions:   
$h^{\text{a}}$, $h^{\text{b}}$ instead of $a$, $b$ for auxiliary variables?  
$x^{\text{start}}$, $x^{\text{skill}}$ instead of $x$, $y$ for decision variables?  
$M^{\text{r}}$ instead of $R$
- Should constants be non-italic ?
- is the approach going in the right direction ?
- bloat constraints ?
- Should symbols be renamed eg machines to $i$ instead of $m$
- Do all seminar participants have to partake in the seminar simultaneously (only 1 starting time for a seminar)

## Notes from second meeting
- Generate Instances (Small for Solvers, Big for heuristics) based on the actual data
- Implement all of these 5
	- MIP
	- Full enumeration
  	- Simulated Annealing
  	- Genetic Algorithm
  	- Priority Rule
- Purge extra seminars from end of machines
- Test + Debug the 5 implementations | next meeting middle of november (after finishing this)
### Notes for thesis from second meeting
- Introduction: Simple for anyone to understand
- Literature review:
	- Learning curve effects (cite how u got to ur learning curve function)
 	- Calculation studies
  	- Design of algorithms
  	- Fit ur research in the current landscape of similar literature
  	- Reasoning
- Main part:
	- Problem description
 	- Example small
  	- Assume you are an OR researcher not familiar with the topic when writing this
  	- Use gantt charts for example and else
  	- Calculation study + results + gantt charts + optimality diff
  	- asymptotic count of variables
  	- managerial insights
- Conclusion: Describe instances and gneeration of those from company data
- Direction for future research: Sync start times of seminars

## Notes before the third meeting
- Generate machines from memory
- Not implementing a priority rule
- Minor bug fixes with SA and GA
- Test full enumeration on small instance sizes
- Ignoring already explored solutions for the heuristics proves to be computationally expensive due to a lot of neighbors being explored and sometimes hitting a dead end with all neighbors having been visited hence needing an alternate strategy where to diverge from that point
- Heuristic GA first -> depth search via SA
- Difficulty of instances (measurement ?)

## Notes from third meeting
- Debugging GUROBI:
	- Timeout set ?
	- Check the log for non optimality
 	- Minimal working example, force optimal solution via setting x variables
- 50-60 Pages
- Code handin via gitlab
- complexity analysis -> dont make any assumptions or non fact based stuffsies
- hyperparameter search + recommendation of best via grid search or similar
- Use gurobi lower bound for optimlaity gap for unsolvable instances

stopping criterion could be based on the max iterations (1% of max iterations without change -> quitting too)
