#!/bin/bash

source ~/python/venv_global/bin/activate

for i in {1..10}
do
    python3 benchmarking.py 4 2 2
done

deactivate