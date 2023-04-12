#!/usr/bin/python3
import json
import os
from typing import Dict, List, Tuple, Any
import plotly.express as px  # type: ignore
import plotly.graph_objects as go  # type:ignore
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

data: Dict[Tuple[float, bool], List[float]] = dict()


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
    bandwidth = content["config"]["bandwidth"]

    attacker = ""
    if content["config"]["teasing_attacker"] > 0:
        attacker += "," if attacker else "" + "teasing-attacker"
    if content["config"]["equivocation_teasing_attacker"] > 0:
        attacker += "," if attacker else "" + "equiv-teasing-attacker"

    if (bandwidth, attacker) not in data:
        data[(bandwidth, attacker)] = []

    data[(bandwidth, attacker)].append(chain_height/run_time)


# compute the traces
print("Computing traces...")

records: List[Dict[str, Any]] = [
    {
        "bandwidth": record[0],
        "attacker": record[1] if record[1] else "no-attack",
        "chain growth": sum(data[record]) / len(data[record]),
        "stdev": np.std(data[record])
    } for record in sorted(list(data))
]


print("Max stdev:", max(records,  key=(lambda x: x["stdev"])))  # type: ignore


# print("Creating plot...")

# fig = px.scatter(records, x="bandwidth", y="chain growth",
#                  # error_y=bw_error_values+delay_error_values,
#                  color="attacker",
#                  labels={
#                      "x": "Bandwidth",
#                      "y": "Rate of chain growth",
#                  }, log_x=args.logx)

# fig.update_layout(legend=dict(
#     yanchor="top",
#     y=0.98,
#     xanchor="left",
#     x=0.02
# ))

out_path = os.path.join(BASE_OUT_PATH, args.data_dir[0])
# out_file = os.path.join(out_path, "fig_exp_teaser.svg")
# out_file2 = os.path.join(out_path, "fig_exp_teaser.png")


# print(f"Saving plot to {out_file}, {out_file2}")
if not os.path.exists(out_path):
    os.mkdir(out_path)
# fig.write_image(out_file)
# fig.write_image(out_file2)


def write_to_csv(filename: str, fields: List[str], x_values: List[Any], y_values: List[Any], delimiter: str = ",") -> None:
    print(f"Saving csv to {filename}")

    with open(filename, 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=delimiter)
        csv_writer.writerow(fields)
        for i in range(len(x_values)):
            csv_writer.writerow(
                [x_values[i], y_values[i]])


write_to_csv(filename=os.path.join(out_path, "fig-experiment-teaser-noattacker-data.txt"),
             fields=["bandwidth", "chain_growth"],
             x_values=[record["bandwidth"]
                       for record in records if record["attacker"] == "no-attack"],
             y_values=[record["chain growth"]
                       for record in records if record["attacker"] == "no-attack"],
             delimiter=" "
             )

write_to_csv(filename=os.path.join(out_path, "fig-experiment-teaser-teasingattacker-data.txt"),
             fields=["bandwidth", "chain_growth"],
             x_values=[record["bandwidth"]
                       for record in records if record["attacker"] == "teasing-attacker"],
             y_values=[record["chain growth"]
                       for record in records if record["attacker"] == "teasing-attacker"],
             delimiter=" "
             )

write_to_csv(filename=os.path.join(out_path, "fig-experiment-teaser-equivteasingattacker-data.txt"),
             fields=["bandwidth", "chain_growth"],
             x_values=[record["bandwidth"]
                       for record in records if record["attacker"] == "equiv-teasing-attacker"],
             y_values=[record["chain growth"]
                       for record in records if record["attacker"] == "equiv-teasing-attacker"],
             delimiter=" "
             )
