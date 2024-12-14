#!/bin/bash

source ~/python/venv_global/bin/activate

for i in {1..30}
do
    python3 benchmarking.py 10 6 4
done

deactivate
