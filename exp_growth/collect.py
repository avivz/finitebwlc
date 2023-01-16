#!/usr/bin/python3
import json
import os
from pprint import pprint
from typing import Dict, List
import plotly.express as px  # type: ignore
import plotly.graph_objects as go  # type:ignore
import numpy as np
import math
import tqdm

BASE_PATH = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
PYTHON_PATH = "python"
DATA_PATH = os.path.join(os.path.split(os.path.abspath(__file__))[0], "data/")

bandwidth_data: Dict[float, List[float]] = dict()
delay_data: Dict[float, List[float]] = dict()

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
    delay = content["config"]["header_delay"]
    if delay > 0:
        if delay not in delay_data:
            delay_data[delay] = []
        delay_data[delay].append(chain_height/run_time)
    else:
        if bandwidth not in bandwidth_data:
            bandwidth_data[bandwidth] = []
        bandwidth_data[bandwidth].append(chain_height/run_time)


# compute the traces
print("Computing traces...")
bw_values = sorted(list(bandwidth_data.keys()))
bw_growth_values = [sum(bandwidth_data[bw])/len(bandwidth_data[bw])
                    for bw in bw_values]
bw_error_values = [np.std(bandwidth_data[bw]) /
                   math.sqrt(len(bandwidth_data[bw])) for bw in bw_values]


delay_values = sorted(list(delay_data.keys()))
adjusted_delay_values = [1/d for d in delay_values]
delay_growth_values = [sum(delay_data[delay])/len(delay_data[delay])
                       for delay in delay_values]
delay_error_values = [np.std(delay_data[delay]) /
                      math.sqrt(len(delay_data[delay])) for delay in delay_values]

print("Max stdev:", max(bw_error_values), max(delay_error_values))
print("Creating plot...")
draw_type = ["Bandwidth Limits"]*len(bw_values) + \
    ["Constant Delay"]*len(adjusted_delay_values)
fig = px.scatter(x=bw_values+adjusted_delay_values, y=bw_growth_values+delay_growth_values,
                 # error_y=bw_error_values+delay_error_values,
                 color=draw_type,
                 labels={
                     "x": "Bandwidth or 1/Delay",
                     "y": "Rate of chain growth",
                     "color": "Block Propagation Model",
                 },)

fig.update_layout(legend=dict(
    yanchor="top",
    y=0.98,
    xanchor="left",
    x=0.02
))

if not os.path.exists("images"):
    os.mkdir("images")
print("Saving plot...")
fig.write_image("images/fig1.png")
