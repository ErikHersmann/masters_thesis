import matplotlib.pyplot as plt
from statistics import mean
import json, sys, glob
from collections import Counter


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

    output_directory = "results/plots/"
    instance_sizes = {}
    cross_validation_histogram = {"genetic_algorithm": [], "simulated_annealing": []}

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

        for algorithm_name in results["solutions"].keys():
            if algorithm_name == "cross_validation_results": continue
            runtime = results["solutions"][algorithm_name]["runtime_seconds"]
            if algorithm_name in results['solutions']['cross_validation_results']:
                cross_validation = results['solutions']["cross_validation_results"][algorithm_name][0]
                cross_validation_histogram[algorithm_name].extend(cross_validation)
            if "lateness" in results["solutions"][algorithm_name].keys():
                lateness = results["solutions"][algorithm_name]["lateness"]
            else:
                lateness = results["solutions"][algorithm_name]["lateness_recalculated"]
            if algorithm_name not in instance_sizes[instance_size]:
                instance_sizes[instance_size][algorithm_name] = [(runtime, lateness)]
            else:
                instance_sizes[instance_size][algorithm_name].append(
                    (runtime, lateness)
                )

    instance_sizes = calculate_means(instance_sizes)
    # Runtime multi line chart
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

    # optimality gap chart
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

    # ALso write something that only uses the instances that have been solved by the exact solvers (or atleast one of the 2) and then plot the absolute optimality gap instance wise, not averaged

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
