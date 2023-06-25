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

selected_files = ["exp_teaser_start_0_1.log",
                  "exp_teaser_start_1_0.log",
                  "exp_teaser_start_2_0.log"
                  ]


def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='collect',
        description='Analyzes results of the experiment',
        fromfile_prefix_chars='@')

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
    block_data = []
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
            block_data.append(
                {"time": record["creation_time"], "height_delta": attacker_height-honest_height})
    return block_data


def sample_data_at_times(block_data: List[Dict[str, Any]], times: List[float]) -> List[Dict[str, Any]]:
    sampled_data = []
    for time in times:
        for block in block_data:
            if block["time"] >= time:
                sampled_data.append(
                    {"time": time, "height_delta": block["height_delta"]})
                break
    return sampled_data


def read_config_file(file_name: str) -> Dict[str, Any]:
    with open(os.path.join(DATA_PATH, file_name), "r") as file:
        config = json.load(file)
        return config  # type: ignore


MAX_TIME = 120
# times = np.arange(0, 120, 1, dtype=float)

plot_data: List[Dict[str, Any]] = list()


print("Reading data...")
for file_name in selected_files:
    if file_name.endswith(".log"):
        config = read_config_file(file_name.replace(".log", ".json"))
        block_data = read_data_from_log(file_name)
        filtered_data = [
            block for block in block_data if block["time"] <= MAX_TIME]
        plot_data.extend(
            dict(config["config"], **sample) for sample in filtered_data
        )

print(plot_data[0], "\n")


print("Plotting...")
# plot a line for each bandwidth x attacker_rate combination

fig = px.line(plot_data, x="time", y="height_delta", color="teasing_attacker",
              )


fig.update_layout(title='Lead of attacker over honest',
                  xaxis_title='Time', yaxis_title='(Attacker Chain - Honest Chain) length')
fig.show()

# create the target directory if it doesn't exist
if not os.path.exists(os.path.join(BASE_OUT_PATH, args.data_dir[0])):
    os.mkdir(os.path.join(BASE_OUT_PATH, args.data_dir[0]))

# Now save a csv file with the data into the results subdir
print("Saving results...")
with open(os.path.join(BASE_OUT_PATH, args.data_dir[0], "exp_teaser_start.csv"), "w") as file:
    file.write("time,height_delta,beta\n")
    for sample in plot_data:
        file.write(
            f"{sample['time']},{sample['height_delta']},{sample['teasing_attacker']}\n")
