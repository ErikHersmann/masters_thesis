# Human resource planning as a parallel machine scheduling problem 
- [Resources](resources/) should contain a file named config.json and a gurobi license file  
- The scripts in [Data generation](data_generation/) can be used to generate the data for running the models/heuristics  
- [benchmarking.py](src/heuristics/benchmarking.py) contains the benchmarking/tool code to compare all metaheuristics and/or exact solvers for a given problem instance, which can be specified in terms of (Jobcount Seminarcount Machinecount) on the commandline or set in the code itself  
- To generate enumeration files for instance sizes one can call [full_enumeration.py](src/heuristics/full_enumeration.py) with the (Jobcount Seminarcount Machinecount) commandline parameters, make sure to not specify an instance size thats too large since its stored in python memory before being written to a file and will therefore be killed by the OOM killer after all available system memory has been used up  
- The other files in [heuristics](src/heuristics) and [solvers](src/solvers) contain the metaheuristic, GUROBI, Full enumeration code and some helper files  
