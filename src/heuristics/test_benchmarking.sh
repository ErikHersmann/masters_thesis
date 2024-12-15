#!/bin/bash

source ~/python/venv_global/bin/activate

for i in {1..10}
do
    python3 benchmarking.py 50 14 15
    python3 benchmarking.py 10 14 4
    python3 benchmarking.py 15 14 3
    python3 benchmarking.py 15 14 5
done

deactivate
