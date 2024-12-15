#!/bin/bash

source ~/python/venv_global/bin/activate

for i in {1..10}
do
    python3 benchmarking.py 10 6 4
    python3 benchmarking.py 15 6 8
done

deactivate
