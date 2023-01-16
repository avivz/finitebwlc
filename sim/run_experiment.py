import dataclasses
from typing import List, Generator, Optional, Tuple, Any, Dict, Union

import argparse
import logging
import sys
import json
import tqdm
import simpy

from .honest_node import HonestNode
from .dumb_attacker import DumbAttacker
from .node import Node
from .mining_oracle import PoWMiningOracle, PoSMiningOracle
from .network import Network
import sim.simulation_parameters as simulation_parameters
from .block import Block
from .teasing_pow_attacker import TeasingPoWAttacker
from .configuration import RunConfig


import plotly.graph_objects as go  # type: ignore
import plotly.express as px  # type: ignore


def plot_timeline(start_time: float, end_time: float, num_nodes: int, download_log: Dict[Node, List[Tuple[Block, float, float]]]) -> None:
    fig = go.Figure()

    width = 0.1
    height = 0.25

    colors = px.colors.qualitative.Alphabet

    # plot download rectangles
    for node in download_log:
        dl_list = download_log[node]
        for block, start, end in dl_list:
            if start > end_time:
                break
            if end < start_time:
                continue
            fig.add_shape(type="rect", xref="x", yref="y", x0=start, x1=end,
                          y0=node.id-height, y1=node.id,
                          fillcolor=colors[hash(block) % len(colors)], line=dict(color="black", width=1), opacity=0.2, layer="below")
            fig.add_annotation(
                x=(start+end)/2, y=node.id - height/2, xref='x', yref='y', text=str(block.id), opacity=0.5,
                showarrow=False)

    # plotting of blocks using markers
    x_vals = [block.creation_time for block in Block.all_blocks if start_time <=
              block.creation_time <= end_time]
    y_vals = [block.miner.id if block.miner else 0 for block in Block.all_blocks if start_time <=
              block.creation_time <= end_time]
    text = [str(block.id) for block in Block.all_blocks if start_time <=
            block.creation_time <= end_time]
    fig.add_trace(go.Scatter(mode="markers+text", x=x_vals, y=y_vals, text=text, textposition="top center", marker_symbol="square",
                             marker_line_color="midnightblue", marker_color="lightskyblue",
                             marker_line_width=2, marker_size=10))
    for block in Block.all_blocks:
        miner_id = block.miner.id if block.miner else 0

        if start_time <= block.creation_time <= end_time:
            if block.parent and block.parent.creation_time >= start_time:
                parent_miner_id = block.parent.miner.id if block.parent.miner else 0
                fig.add_annotation(
                    x=block.parent.creation_time+width, y=parent_miner_id,
                    ax=block.creation_time-width, ay=miner_id,
                    xref='x', yref='y', axref='x', ayref='y', text='',
                    showarrow=True, arrowhead=3, arrowsize=1, arrowwidth=1, arrowcolor='black')

    # Set axes ranges
    fig.update_xaxes(
        range=[start_time - width, end_time + width], showgrid=False, zeroline=False)
    fig.update_yaxes(range=[0 - height, num_nodes -
                     1 + height], dtick=1, tick0=1, showgrid=False, zeroline=False,
                     tickvals=list(range(num_nodes)), ticktext=[f"Node {i}" for i in range(num_nodes)], tickmode="array")
    fig.update_layout(xaxis_title="time (sec)")
    fig.show()


class MyParser(argparse.ArgumentParser):
    @staticmethod
    def convert_arg_line_to_args(arg_line: str) -> List[str]:
        return arg_line.split()


def setup_parser() -> argparse.ArgumentParser:
    parser = MyParser(
        prog='run_experiment',
        description='Run a basic experiment of the mining simulation.\nSpecify a configuration file with @<filename>.',
        fromfile_prefix_chars='@')

    parser.add_argument("--" + RunConfig.VERBOSE,
                        action='store_true', help="print events to stdout")

    parser.add_argument('--' + RunConfig.PLOT, nargs=2, type=int, metavar=('START', 'END'),
                        help="plot a block diagram from <START> to <END> times")

    parser.add_argument("--" + RunConfig.MODE, choices=[
                        'pos', 'pow'], help="which mode of operation we are using", required=True)

    parser.add_argument("--" + RunConfig.POS_ROUND_LENGTH, metavar="SECs",
                        help="How long the mining round is in PoS (valid only in PoS mode, defaults to 1sec)",
                        type=float, default=1)

    parser.add_argument("--" + RunConfig.DUMB_ATTACKER, metavar="MINING_POWER",
                        help="include an attacker with the given mining power (defaults to no attacker)",
                        type=float, default=0)

    parser.add_argument("--" + RunConfig.TEASING_ATTACKER, metavar="MINING_POWER", type=float,
                        help="include a teasing attacker with the given mining power (defaults to no attacker)",
                        default=0)

    parser.add_argument("--" + RunConfig.ATTACKER_HEAD_START, metavar="NUM_BLOCKS", type=int,
                        help="give any attacker NUM_BLOCKS mining at the begining of the simulation. This only matters if an attacker is present.",
                        default=0)

    parser.add_argument("--" + RunConfig.RUN_TIME, default=100, required=True, type=float,
                        help="time to run")

    parser.add_argument("--" + RunConfig.NUM_HONEST, default=10, required=True, type=int,
                        help="number of honest nodes")

    parser.add_argument("--" + RunConfig.HONEST_BLOCK_RATE, default=0.1, required=True, type=float,
                        help="mining power of each honest node")

    parser.add_argument("--" + RunConfig.BANDWIDTH, default=1, required=True, type=float,
                        help="bandwidth of each honest node")

    parser.add_argument("--" + RunConfig.HEADER_DELAY, default=0, required=True, type=float,
                        help="header_delay header delay of each honest node")

    parser.add_argument('--' + RunConfig.SAVE_RESULTS, default="", type=str,
                        help="filename (Where to save the results of the simulation)")
    return parser


class Experiment:
    def __init__(self, run_config: RunConfig) -> None:
        self.__config = run_config

        self.__download_log: Optional[Dict[Node,
                                           List[Tuple[Block, float, float]]]] = None
        if self.__config.plot:
            self.__download_log = {}

        self.__network = Network(self.__download_log)
        self.__nodes: List[Node] = []

        if run_config.dumb_attacker:
            attacker = DumbAttacker(run_config.dumb_attacker, self.__network)
            self.__nodes.append(attacker)
            for i in range(run_config.attacker_head_start):
                attacker.mine_block(i+1)

        if run_config.teasing_attacker:
            attacker2 = TeasingPoWAttacker(
                run_config.teasing_attacker, self.__network)
            self.__nodes.append(attacker2)
            for i in range(run_config.attacker_head_start):
                attacker2.mine_block(i+1)

        self.__nodes += [HonestNode(mining_rate=run_config.honest_block_rate,
                                    bandwidth=run_config.bandwidth,
                                    header_delay=run_config.header_delay,
                                    network=self.__network)
                         for _ in range(run_config.num_honest)]

        if run_config.mode == "pow":
            self.__mining_oracle: Union[PoWMiningOracle,
                                        PoSMiningOracle] = PoWMiningOracle(self.__nodes)
        else:
            self.__mining_oracle = PoSMiningOracle(
                self.__nodes, run_config.pos_round_length, run_config.attacker_head_start)
        self.__run_time = run_config.run_time

    def run_experiment(self, progress_bar: bool = True) -> None:
        """a basic experiment with 10 nodes mining together at a rate of 1 block per second"""
        if progress_bar:
            setup_progress_bar(self.__run_time)
        simulation_parameters.ENV.run(until=self.__run_time)
        if self.__config.plot is not None:
            assert self.__download_log is not None
            plot_timeline(
                start_time=self.__config.plot[0], end_time=self.__config.plot[1],
                num_nodes=len(self.__nodes), download_log=self.__download_log)


def setup_progress_bar(run_time: float, num_updates: int = 100) -> None:
    def progress_bar_process() -> Generator[simpy.events.Event, None, None]:
        with tqdm.tqdm(total=run_time, disable=None, unit="sim_secs") as pbar:
            for i in range(num_updates):
                yield simulation_parameters.ENV.timeout(run_time/num_updates)
                pbar.update(run_time/num_updates)
    simulation_parameters.ENV.process(progress_bar_process())


def calc_honest_chain_height() -> int:
    for block in reversed(Block.all_blocks):
        if type(block.miner) == HonestNode:
            return block.height
    return 0


if __name__ == "__main__":
    parser = setup_parser()
    run_config = RunConfig()
    parser.parse_args(namespace=run_config)

    if run_config.verbose:
        logger = logging.getLogger("SIM_INFO")
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

    experiment = Experiment(run_config)
    experiment.run_experiment()

    honest_chain_height = calc_honest_chain_height()

    result: Dict[str, Any] = {}
    result["config"] = dataclasses.asdict(run_config)
    result["honest_chain_height"] = honest_chain_height

    # write the results to stdout or file:
    if run_config.save_results:
        file_name = run_config.save_results
        with open(file_name, 'w') as out_file:
            json.dump(result, out_file, indent=2)
    else:
        json.dump(result, sys.stdout, indent=2)
