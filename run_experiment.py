from honest_node import HonestNode
from node import Node
from typing import List
from mining_oracle import PoWMiningOracle
from network import Network
import argparse
import simulation_parameters
import cProfile
import plotly.express as px  # type: ignore
import pandas as pd  # type: ignore
from block import Block
import plotly.graph_objects as go  # type: ignore


def run_experiment(num_nodes: int, honest_block_rate: float, bandwidth: float, header_delay: float) -> None:
    """a basic experiment with 10 nodes mining together at a rate of 1 block per second"""
    network = Network()

    nodes: List[Node] = [HonestNode(mining_rate=honest_block_rate,
                                    bandwidth=bandwidth,
                                    header_delay=header_delay,
                                    network=network)
                         for _ in range(num_nodes)]

    PoWMiningOracle(nodes)

    simulation_parameters.ENV.run(until=100)


def plot_timeline(start_time: float, end_time: float, num_nodes: int) -> None:
    fig = go.Figure()

    width = 0.1
    height = 0.25

    # Set axes ranges
    fig.update_xaxes(range=[start_time - width, end_time + width])
    fig.update_yaxes(range=[0 - height, num_nodes + height], dtick=1, tick0=1)

    # alternative plotting of blocks using markers
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
            # draw a rectangle for the block
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='basic_experiment',
        description='Run a basic experiment of the mining simulation')

    parser.add_argument('-v', '--verbose',
                        action='store_true', help="print events to stdout")  # on/off flag

    parser.add_argument('--plot',
                        action='store_true', help="plot a block diagram")  # on/off flag

    parser.add_argument('--num_honest', nargs=1, required=True, type=int,
                        help="-num_honest <number of honest nodes>")

    parser.add_argument('--pow_honest', nargs=1, required=True, type=float,
                        help="-pow_honest <mining power of each honest node>")

    parser.add_argument('--bandwidth', nargs=1, required=True, type=float,
                        help="-bandwidth <bandwidth of each honest node>")

    parser.add_argument('--header_delay', nargs=1, required=True, type=float,
                        help="-header_delay <header delay of each honest node>")

    args = parser.parse_args()
    simulation_parameters.verbose = args.verbose
    run_experiment(int(args.num_honest[0]), float(
        args.pow_honest[0]), float(args.bandwidth[0]), float(args.header_delay[0]))
    if args.plot:
        plot_timeline(start_time=0, end_time=100, num_nodes=args.num_honest[0])
