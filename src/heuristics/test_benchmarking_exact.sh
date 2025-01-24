#!/bin/bash

source ~/python/venv_global/bin/activate

j_values=(3 4)
s_values=(2)
m_values=(2)

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
