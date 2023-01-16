#!/usr/bin/python3
import json
import os
from typing import Dict, List, Tuple, Any
import plotly.express as px  # type: ignore
import plotly.graph_objects as go  # type:ignore
import numpy as np
import tqdm
import csv

BASE_PATH = os.path.split(os.path.abspath(__file__))[0]
PYTHON_PATH = "python"
DATA_PATH = os.path.join(BASE_PATH, "data/")

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
    attacker = bool(content["config"]["teasing_attacker"] > 0)
    if (bandwidth, attacker) not in data:
        data[(bandwidth, attacker)] = []
    data[(bandwidth, attacker)].append(chain_height/run_time)


# compute the traces
print("Computing traces...")

records: List[Dict[str, Any]] = [
    {
        "bandwidth": record[0],
        "attacker": "active attacker" if record[1] else "no attacker",
        "chain growth": sum(data[record]) / len(data[record]),
        "stdev": np.std(data[record])
    } for record in sorted(list(data))
]


print("Max stdev:", max(records,  key=(lambda x: x["stdev"])))  # type: ignore

print("Creating plot...")

fig = px.scatter(records, x="bandwidth", y="chain growth",
                 # error_y=bw_error_values+delay_error_values,
                 color="attacker",
                 labels={
                     "x": "Bandwidth",
                     "y": "Rate of chain growth",
                 },)

fig.update_layout(legend=dict(
    yanchor="top",
    y=0.98,
    xanchor="left",
    x=0.02
))

out_path = os.path.join(BASE_PATH, "results/")
out_file = os.path.join(out_path, "fig_exp_teaser.svg")

print(f"Saving plot to {out_file}")
if not os.path.exists(out_path):
    os.mkdir(out_path)
fig.write_image(out_file)

csv_file = os.path.join(out_path, "exp_teaser.csv")

print(f"Saving csv to {csv_file}")

with open(csv_file, 'w') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["x_bandwidth", "y_chain_growth", "attacker"])
    for record in records:
        csv_writer.writerow(
            [record["bandwidth"], record["chain growth"], record["attacker"]])
