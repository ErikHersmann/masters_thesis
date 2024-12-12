import json, sys

if __name__ == "__main__":
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        filename = "results/benchmark/1733439627_benchmark.json"

    with open(filename, "r") as f:
        results = json.load(f)
    print(results['solutions'].keys())
