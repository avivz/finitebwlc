#!/usr/bin/python3
from typing import List, Dict, Any
import json
import os
from typing import Dict, List, Tuple, Any
import plotly.express as px  # type: ignore
import plotly.graph_objects as go  # type:ignore
import numpy as np
import argparse

BASE_PATH = os.path.split(os.path.abspath(__file__))[0]
PYTHON_PATH = "python"
BASE_DATA_PATH = os.path.join(BASE_PATH, "data/")


def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='collect',
        description='Analyzes results of the experiment',
        fromfile_prefix_chars='@')

    # parser.add_argument('--logx',
    #                     action='store_true', help="makes x axis logscale")  # on/off flag

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


def read_data_from_log(file_name: str) -> List[Dict[str, Any]]:
    attacker_height = 0
    honest_height = 0
    plot_data = []
    with open(os.path.join(DATA_PATH, file_name), "r") as file:
        lines = file.readlines()
        for line in lines:
            record = json.loads(line)
            # a sample record: {"creation_time": 7.828518669918317, "miner": 0, "parent": "6.1", "height": 7, "block_id": "7.1"}
            if record["miner"] == 0:
                attacker_height = record["height"]
            elif record["height"] > honest_height:
                honest_height = record["height"]
                if honest_height > attacker_height:
                    attacker_height = honest_height
            plot_data.append(
                {"time": record["creation_time"], "height_delta": attacker_height-honest_height})
    return plot_data


def get_trace_averages(base_file_name: str, times: np.ndarray[Any, np.dtype[Any]]) -> List[float]:

    single_trace_data = []
    for i in range(10):
        file_name = base_file_name+str(i)+".log"
        plot_data = read_data_from_log(file_name)
        single_trace_data.append(plot_data)

    average_of_deltas = []
    print("Processing data...")
    for time in times:
        deltas = []
        for plot_data in single_trace_data:
            for record in plot_data:
                if record["time"] > time:
                    deltas.append(record["height_delta"])
                    break
        average_of_deltas.append(np.mean(deltas))
    return average_of_deltas


base_file_name = "exp2_teaser_"
times = np.arange(0, 400, 1, dtype=float)

print("Plotting...")
fig = go.Figure()
for i in range(4):
    file_name = base_file_name+str(i)+"_"
    average_of_deltas = get_trace_averages(file_name, times)

    fig.add_trace(go.Scatter(x=times, y=average_of_deltas,
                             mode='lines',
                             name=file_name))

fig.update_layout(title='Average Lead of attacker over honest',
                  xaxis_title='Time', yaxis_title='Average (Attacker Chain - Honest Chain) length')
fig.show()
