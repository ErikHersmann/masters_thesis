#!/bin/bash

source ~/python/venv_global/bin/activate

j_values=(20 50 100)
# 20
s_values=(0 5 14)
m_values=(2 5 10)

for j in "${j_values[@]}"; do
    for s in "${s_values[@]}"; do
        for m in "${m_values[@]}"; do
			for i in {1..10}; do
            	python3 benchmarking.py $j $s $m
			done
        done
    done
done

deactivate
