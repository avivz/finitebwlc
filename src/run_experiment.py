import dataclasses
from typing import List, Generator, Optional, Tuple, Any, Dict

import argparse
import logging
import sys
import json
import tqdm
import simpy

from honest_node import HonestNode
from dumb_attacker import DumbAttacker
from node import Node
from mining_oracle import PoWMiningOracle
from network import Network
import simulation_parameters
from block import Block


import plotly.graph_objects as go  # type: ignore


def plot_timeline(start_time: float, end_time: float, num_nodes: int) -> None:
    fig = go.Figure()

    width = 0.1
    height = 0.25

    # Set axes ranges
    fig.update_xaxes(range=[start_time - width, end_time + width])
    fig.update_yaxes(range=[0 - height, num_nodes + height], dtick=1, tick0=1)

    # plotting of blocks using markers
    x_vals = [block.creation_time for block in Block.all_blocks if start_time <=
              block.creation_time <= end_time]
    y_vals = [block.miner.id if block.miner else 0 for block in Block.all_blocks if start_time <=
              block.creation_time <= end_time]
    text = [str(block.height) for block in Block.all_blocks if start_time <=
            block.creation_time <= end_time]
    fig.add_trace(go.Scatter(mode="markers+text", x=x_vals, y=y_vals, text=text, textposition="top center", marker_symbol="square",
                             marker_line_color="midnightblue", marker_color="lightskyblue",
                             marker_line_width=2, marker_size=10,))
    for block in Block.all_blocks:
        miner_id = block.miner.id if block.miner else 0

        if start_time <= block.creation_time <= end_time:
            # Alternative: draw a rectangle for the block
            # fig.add_shape(type="rect", xref="x", yref="y", x0=block.creation_time - width,
            #               x1=block.creation_time+width,
            #               y0=miner_id-height, y1=miner_id+height, fillcolor="blue",)

            # draw an arrow from the block to its parent
            if block.parent and block.parent.creation_time >= start_time:
                parent_miner_id = block.parent.miner.id if block.parent.miner else 0
                fig.add_annotation(
                    x=block.parent.creation_time+width, y=parent_miner_id,
                    ax=block.creation_time-width, ay=miner_id,
                    xref='x', yref='y', axref='x', ayref='y', text='',
                    showarrow=True, arrowhead=3, arrowsize=1, arrowwidth=1, arrowcolor='black')

    fig.update_layout(
        xaxis_title="time (sec)",
        yaxis_title="Node ID",
    )
    fig.show()


@dataclasses.dataclass
class RunConfig:
    run_time: float
    num_honest: int
    honest_block_rate: float
    bandwidth: float
    header_delay: float
    attacker_power: float
    plotting: Optional[Tuple[float, float]]


class MyParser(argparse.ArgumentParser):
    @staticmethod
    def convert_arg_line_to_args(arg_line: str) -> List[str]:
        return arg_line.split()


def setup_parser() -> argparse.ArgumentParser:
    parser = MyParser(
        prog='run_experiment',
        description='Run a basic experiment of the mining simulation.\nSpecify a configuration file with @<filename>.',
        fromfile_prefix_chars='@')

    parser.add_argument('-v', '--verbose',
                        action='store_true', help="print events to stdout")  # on/off flag

    parser.add_argument('--plot', nargs=2, type=int, metavar=('START', 'END'),
                        help="plot a block diagram from <START> to <END> times")  # on/off flag

    parser.add_argument('--attacker_power', metavar="MINING_POWER",
                        help="include an attacker with the given mining power (defaults to no attacker)", type=float, default=0)  # on/off flag

    parser.add_argument('--run_time', nargs=1, required=True, type=float,
                        help="time to run")

    parser.add_argument('--num_honest', nargs=1, required=True, type=int,
                        help="number of honest nodes")

    parser.add_argument('--pow_honest', nargs=1, required=True, type=float,
                        help="mining power of each honest node")

    parser.add_argument('--bandwidth', nargs=1, required=True, type=float,
                        help="bandwidth of each honest node")

    parser.add_argument('--header_delay', nargs=1, required=True, type=float,
                        help="header_delay header delay of each honest node")

    parser.add_argument('--saveResults', nargs=1, type=argparse.FileType('w'),
                        help="filename (Where to save the results of the simulation)")
    return parser


class Experiment:
    def __init__(self, run_config: RunConfig) -> None:
        self.network = Network()
        self.nodes: List[Node] = []
        if run_config.attacker_power:
            self.nodes.append(DumbAttacker(
                run_config.attacker_power, self.network))
        self.nodes += [HonestNode(mining_rate=run_config.honest_block_rate,
                                  bandwidth=run_config.bandwidth,
                                  header_delay=run_config.header_delay,
                                  network=self.network)
                       for _ in range(run_config.num_honest)]
        self.mining_oracle = PoWMiningOracle(self.nodes)
        self.run_time = run_config.run_time
        setup_progress_bar(self.run_time)

    def run_experiment(self) -> None:
        """a basic experiment with 10 nodes mining together at a rate of 1 block per second"""
        simulation_parameters.ENV.run(until=self.run_time)


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
    args = parser.parse_args()

    if args.verbose:
        logger = logging.getLogger("SIM_INFO")
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

    run_config = RunConfig(
        run_time=args.run_time[0],
        num_honest=args.num_honest[0],
        honest_block_rate=args.pow_honest[0],
        bandwidth=args.bandwidth[0],
        header_delay=args.header_delay[0],
        attacker_power=args.attacker_power,
        plotting=args.plot if args.plot else None
    )

    experiment = Experiment(run_config)
    experiment.run_experiment()

    honest_chain_height = calc_honest_chain_height()

    result: Dict[str, Any] = {}
    result["config"] = dataclasses.asdict(run_config)
    result["honest_chain_height"] = honest_chain_height

    # write the results to stdout or file:
    if args.saveResults:
        json.dump(result, args.saveResults[0], indent=2)
    else:
        json.dump(result, sys.stdout, indent=2)

    if args.plot:
        plot_timeline(
            start_time=args.plot[0], end_time=args.plot[1], num_nodes=args.num_honest[0])
