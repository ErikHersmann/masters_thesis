import matplotlib.pyplot as plt
from statistics import mean
import json, sys, glob
from collections import Counter
from pyperclip import copy as copy_to_clipboard
import numpy as np


def calculate_means(data):
    transformed_data = {}
    for key, sub_dict in data.items():
        transformed_data[key] = {}
        for sub_key, tuples in sub_dict.items():
            filtered_tuples = [
                (x, y) for x, y in tuples if x is not None and y is not None
            ]
            if filtered_tuples:
                mean_first = mean(x for x, _ in filtered_tuples)
                mean_second = mean(y for _, y in filtered_tuples)
                transformed_data[key][sub_key] = (mean_first, mean_second)
            else:
                transformed_data[key][sub_key] = (None, None)
    return transformed_data


if __name__ == "__main__":
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        filename = "results/benchmark/1733439627_benchmark.json"

    output_directory = "results/"
    instance_sizes = {}
    cross_validation_histogram = {"genetic_algorithm": [], "simulated_annealing": []}
    lateness_averages = {}
    mapping_algo_names = {
        "genetic_algorithm": 0,
        "simulated_annealing": 1,
        "hybrid_algorithm": 2,
        "gurobi": 5,
        "full_enumeration": 6
    }

    for filename in glob.glob("results/benchmark/*_benchmark.json"):
        # For averaging purposes

        with open(filename, "r") as f:
            results = json.load(f)

        instance_size = (
            sum([1 for cand in results["jobs_seminars"] if cand["type"] == "job"]),
            sum([1 for cand in results["jobs_seminars"] if cand["type"] == "seminar"]),
            len(results["machines"]),
        )
        if instance_size not in instance_sizes:
            instance_sizes[instance_size] = {}
            lateness_averages[instance_size] = [[] for _ in range(7)]

        for algorithm_name in results["solutions"].keys():
            # input(results['solutions'].keys())
            if algorithm_name == "cross_validation_results":
                cv_ga_lateness = results["solutions"][algorithm_name][
                    "genetic_algorithm"
                ][1]
                cv_sa_lateness = results["solutions"][algorithm_name][
                    "simulated_annealing"
                ][1]
                lateness_averages[instance_size][3].append(cv_ga_lateness)
                lateness_averages[instance_size][4].append(cv_sa_lateness)
                continue
            runtime = results["solutions"][algorithm_name]["runtime_seconds"]
            if algorithm_name in results["solutions"]["cross_validation_results"]:
                cross_validation = results["solutions"]["cross_validation_results"][
                    algorithm_name
                ][0]
                cross_validation_histogram[algorithm_name].extend(cross_validation)
            if "lateness" in results["solutions"][algorithm_name].keys():
                lateness = results["solutions"][algorithm_name]["lateness"]
            else:
                lateness = results["solutions"][algorithm_name]["lateness_recalculated"]

            if algorithm_name not in ["full_enumeration", "gurobi"]:
                lateness_averages[instance_size][
                    mapping_algo_names[algorithm_name]
                ].append(lateness)
            elif algorithm_name in ["full_enumeration", "gurobi"] and lateness != None:
                lateness_averages[instance_size][mapping_algo_names[algorithm_name]].append(lateness)
            if algorithm_name not in instance_sizes[instance_size]:
                instance_sizes[instance_size][algorithm_name] = [(runtime, lateness)]
            else:
                instance_sizes[instance_size][algorithm_name].append(
                    (runtime, lateness)
                )
    for instance_size in instance_sizes.keys():
        print(instance_size)
        for x in instance_sizes[instance_size]:
            print(x,f"{(20 - len(x)) * ' '}", [ y[1] for y in instance_sizes[instance_size][x]])

    output_string = []
    for instance_size, item in lateness_averages.items():
        if len(item[5]) > 0:
            gurobi_string = round(mean(item[5]), 1)
        else: 
            gurobi_string = "-"
        if len(item[6]) > 0:
            full_enum_string = round(mean(item[6]), 1)
            latex_string = "\\textsuperscript{*} "
        else:
            full_enum_string = "-"
            latex_string = ""
        cur_string = f"J{instance_size[0]}S{instance_size[1]}M{instance_size[2]}{latex_string} & {gurobi_string} & {full_enum_string} & {round(mean(item[0]), 1)} & {round(mean(item[1]), 1)} & {round(mean(item[2]), 1)} & {round(mean(item[3]), 1)} & {round(mean(item[4]), 1)} \\\\"
        # print(cur_string)
        if full_enum_string != "-":
            output_string.insert(0, cur_string)
        else:
            output_string.append(cur_string)
    output_string[-1] = output_string[-1][:-2]
    copy_to_clipboard("\n".join(output_string))
    print("\n".join(output_string))

    instance_sizes = calculate_means(instance_sizes)

    ################
    # RUNTIME CHART#
    ################
    plt.figure(figsize=(10, 6))
    for algorithm_name in list(instance_sizes[list(instance_sizes.keys())[0]].keys()):
        plt.plot(
            list(range(len(instance_sizes.keys()))),
            [
                x[algorithm_name][0]
                for x in instance_sizes.values()
                if algorithm_name in x
            ],
            marker="o",
            label=algorithm_name,
        )
    plt.yscale("log")
    plt.xlabel("Instance Size (Job, Seminar, Machine)")
    plt.ylabel("Runtime (seconds)")
    plt.title("Average Algorithm Runtimes by Instance Size")
    plt.xticks(
        rotation=45,
        ticks=list(range(len(instance_sizes.keys()))),
        labels=[str(x) for x in list(instance_sizes.keys())],
    )
    plt.legend(title="Algorithm")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(f"{output_directory}algorithm_runtimes.png")

    #################
    # LATENESS CHART#
    #################
    plt.clf()
    plt.figure(figsize=(10, 6))
    for algorithm_name in list(instance_sizes[list(instance_sizes.keys())[0]].keys()):
        plt.plot(
            list(range(len(instance_sizes.keys()))),
            [
                x[algorithm_name][1]
                for x in instance_sizes.values()
                if algorithm_name in x
            ],
            marker="o",
            label=algorithm_name,
        )
    plt.xlabel("Instance Size (Job, Seminar, Machine)")
    plt.ylabel("Lateness")
    plt.title("Average Algorithm Lateness by Instance Size")
    plt.xticks(
        rotation=45,
        ticks=list(range(len(instance_sizes.keys()))),
        labels=[str(x) for x in list(instance_sizes.keys())],
    )
    plt.legend(title="Algorithm")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{output_directory}algorithm_lateness.png")
    plt.clf()

    ##########################################
    # EXACT SOLVER DIFFERENCE METAHEURISTICS #
    ##########################################
    differences = {}
    algorithm_names = []
    for key, value in instance_sizes.items():
        if "full_enumeration" not in value.keys():
            continue
        full_enum_lateness = value['full_enumeration'][1]
        if full_enum_lateness == None: continue
        differences[key] = {}
        for algo, tup in value.items():
            if tup == (None, None): continue
            differences[key][algo] = tup[1] - full_enum_lateness
            if algo not in algorithm_names: algorithm_names.append(algo)

    plt.clf()
    plt.figure(figsize=(12, 8))
    x = np.arange(len(differences)) * 1.2  
    width = 0.2 
    for i, algorithm_name in enumerate(algorithm_names):
        y_values = [
            (
                differences[instance][algorithm_name] + 0.05
                if algorithm_name in differences[instance]
                else 0
            )
            for instance in differences.keys()
        ]
        plt.bar(
            x + i * width,
            y_values,
            width,
            label=algorithm_name,
        )
    plt.xlabel("Instance Size (Job, Seminar, Machine)")
    plt.ylabel("Lateness Difference To Exact Methods")
    plt.title("Average Algorithm Lateness Difference To Exact Methods by Instance Size")
    plt.xticks(
    ticks=x + (len(algorithm_names) - 1) * width / 2,
    labels=list(differences.keys()),
    rotation=45
    )
    plt.legend(title="Algorithm")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{output_directory}algorithm_lateness_differences.png")
    plt.clf()

    ###############################
    # HYPERPARAMETER SEARCH CHART #
    ###############################
    fig, axes = plt.subplots(2, 1, figsize=(12, 9))

    for ax, (method, data) in zip(axes, cross_validation_histogram.items()):
        counts = Counter(data)
        counts = {key: value for key, value in counts.items() if value > 1}
        labels = list(counts.keys())
        values = list(counts.values())
        ax.bar(labels, values, color="skyblue")
        ax.set_title(f"Histogram for {method}")
        ax.set_xlabel("Parameters")
        ax.set_ylabel("Frequency")
        ax.tick_params(axis="x", rotation=90)
    plt.tight_layout()
    plt.savefig(f"{output_directory}cross_val_histogram.png")
