#!/usr/bin/python3
import json
import os
from typing import Dict, List, Tuple, Any
import plotly.express as px  # type: ignore
import plotly.graph_objects as go  # type: ignore
import numpy as np
import tqdm
import csv
import argparse

BASE_PATH = os.path.split(os.path.abspath(__file__))[0]
PYTHON_PATH = "python"
BASE_DATA_PATH = os.path.join(BASE_PATH, "data/")


def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='collect',
        description='Analyzes results of the experiment',
        fromfile_prefix_chars='@')

    parser.add_argument('--logx',
                        action='store_true', help="makes x axis logscale")  # on/off flag

    parser.add_argument('--data_dir',
                        nargs=1, help="where to find results within the data directory", required=True, type=str)

    return parser


parser = setup_parser()
args = parser.parse_args()


DATA_PATH = os.path.join(BASE_DATA_PATH, args.data_dir[0])
BASE_OUT_PATH = os.path.join(BASE_PATH, "results/")
if not os.path.exists(BASE_OUT_PATH):
    os.mkdir(BASE_OUT_PATH)

data: Dict[Tuple[float, str], Tuple[List[float], List[float]]] = dict()


# read data from files
print("Reading files...")
for file_name in tqdm.tqdm(os.listdir(DATA_PATH)):
    if not file_name.endswith(".json"):
        continue
    try:
        with open(os.path.join(DATA_PATH, file_name), 'r') as file:
            content = json.load(file)
    except:
        print("FAILED to read", file_name)

    run_time = content["config"]["run_time"]
    chain_height = content["honest_chain_height"]
    ancestor_height = content["honest_chain_common_ancestor_height"]
    bandwidth = content["config"]["bandwidth"]
    download_rule = content["config"]["download_rule"]
    if (bandwidth, download_rule) not in data:
        data[(bandwidth, download_rule)] = [], []
    data[(bandwidth, download_rule)][0].append(chain_height/run_time)
    data[(bandwidth, download_rule)][1].append(ancestor_height/run_time)


# compute the traces
print("Computing traces...")

records: List[Dict[str, Any]] = [
    {
        "bandwidth": key_record[0],
        "download_rule":key_record[1],
        "chain growth": sum(data[key_record][0]) / len(data[key_record][0]),
        "stdev_cg": np.std(data[key_record][0]),
        "max ancestor height": sum(data[key_record][1]) / len(data[key_record][1]),
        "stdev_mah": np.std(data[key_record][1]),
    } for key_record in sorted(list(data))
]


print("Max stdev chain growth:", max(
    records,  key=(lambda x: x["stdev_cg"])))  # type: ignore
print("Max stdev ancestor height:", max(
    records,  key=(lambda x: x["stdev_mah"])))  # type: ignore

print("Creating plot...")

fig = px.scatter(records, x="bandwidth", y="max ancestor height",
                 color="download_rule",
                 labels={
                     "x": "Bandwidth",
                     "y": "Rate of chain growth",
                 }, log_x=args.logx)

fig.update_layout(legend=dict(
    yanchor="top",
    y=0.98,
    xanchor="left",
    x=0.02
))

out_path = os.path.join(BASE_OUT_PATH, args.data_dir[0])
out_file = os.path.join(out_path, "fig_exp_greedy.svg")
out_file2 = os.path.join(out_path, "fig_exp_greedy.png")


print(f"Saving plot to {out_file}, {out_file2}")
if not os.path.exists(out_path):
    os.mkdir(out_path)
fig.write_image(out_file)
fig.write_image(out_file2)


def write_to_csv(filename: str, fields: List[str], x_values: List[Any], y_values: List[Any], delimiter: str = ",") -> None:
    print(f"Saving csv to {filename}")

    with open(filename, 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=delimiter)
        csv_writer.writerow(fields)
        for i in range(len(x_values)):
            csv_writer.writerow(
                [x_values[i], y_values[i]])


write_to_csv(filename=os.path.join(out_path, "fig-experiment-greedy-greedydl-data.txt"),
             fields=["bandwidth", "max_ancestor_height"],
             x_values=[record["bandwidth"]
                       for record in records if record["download_rule"] == "greedy_extend_chain"],
             y_values=[record["max ancestor height"]
                       for record in records if record["download_rule"] == "greedy_extend_chain"],
             delimiter=" "
             )

write_to_csv(filename=os.path.join(out_path, "fig-experiment-greedy-longestdl-data.txt"),
             fields=["bandwidth", "max_ancestor_height"],
             x_values=[record["bandwidth"]
                       for record in records if record["download_rule"] == "longest_header_chain"],
             y_values=[record["max ancestor height"]
                       for record in records if record["download_rule"] == "longest_header_chain"],
             delimiter=" "
             )
