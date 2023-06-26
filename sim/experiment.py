
import dataclasses
from typing import List, Generator, Optional, Tuple, Any, Dict, Union

import tqdm
import simpy
import os

from .honest_node_longest_header_chain import HonestNodeLongestHeaderChain
from .honest_node_greedy_chain import HonestNodeGreedy
from .dumb_attacker import DumbAttacker
from .private_attacker import PrivateAttacker
from .node import Node
from .mining_oracle import PoWMiningOracle  # , PoSMiningOracle
from .network import Network
from .block import Block
from .teasing_pow_attacker import TeasingPoWAttacker
from .equivocation_teasing_pow_attacker import EquivocationTeasingPoWAttacker
from .configuration import RunConfig, DownloadRules


BASE_PATH = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]


class Experiment:
    def __init__(self, run_config: RunConfig) -> None:
        self.__config = run_config
        self.__env = simpy.core.Environment()
        # pass the environment to the nodes for logging purposes.
        Node.env = self.__env

        self.__download_log: Optional[Dict[Node,
                                           List[Tuple[Block, float, float]]]] = None
        if self.__config.plot:
            self.__download_log = {}

        self.__network = Network(self.__env, self.__download_log)
        self.__all_nodes: List[Node] = []
        self.__honest_nodes: List[Node]

        self.__genesis = Block(None, None, 0)

        self._create_all_nodes()

        if run_config.mode == "pow":
            self.__mining_oracle = PoWMiningOracle(
                self.__env, self.__all_nodes)
        else:
            # self.__mining_oracle = PoSMiningOracle(self.__env,
            #                                        self.__all_nodes, run_config.pos_round_length, run_config.attacker_head_start)
            raise NotImplementedError("PoS is not fully implemented.")
        self.__run_time = run_config.run_time

    def _create_all_nodes(self) -> None:
        if self.__config.dumb_attacker:
            attacker = DumbAttacker(
                self.__genesis, self.__config.dumb_attacker, self.__network)
            self.__all_nodes.append(attacker)
            for i in range(self.__config.attacker_head_start):
                attacker.mine_block()

        if self.__config.private_attacker:
            attacker2 = PrivateAttacker(
                self.__genesis, self.__config.private_attacker, self.__network)
            self.__all_nodes.append(attacker2)
            for i in range(self.__config.attacker_head_start):
                attacker2.mine_block()

        if self.__config.teasing_attacker:
            attacker3 = TeasingPoWAttacker(self.__genesis,
                                           self.__config.teasing_attacker,
                                           self.__network)
            self.__all_nodes.append(attacker3)
            for i in range(self.__config.attacker_head_start):
                attacker3.mine_block()

        if self.__config.equivocation_teasing_attacker:
            attacker4 = EquivocationTeasingPoWAttacker(self.__genesis,
                                                       self.__config.equivocation_teasing_attacker,
                                                       self.__network)
            self.__all_nodes.append(attacker4)
            for i in range(self.__config.attacker_head_start):
                attacker4.mine_block()

        if self.__config.download_rule == DownloadRules.LongestHeaderChain.value:
            def node_factory() -> Node:
                return HonestNodeLongestHeaderChain(self.__genesis, self.__config.honest_block_rate, self.__config.bandwidth,
                                                    self.__config.header_delay, self.__network)
        elif self.__config.download_rule == DownloadRules.GreedyExtendChain.value:
            def node_factory() -> Node:
                return HonestNodeGreedy(self.__genesis, self.__config.honest_block_rate, self.__config.bandwidth,
                                        self.__config.header_delay, self.__network)
        else:
            raise ValueError("Unsupported download rule:" +
                             str(self.__config.download_rule))

        self.__honest_nodes = [node_factory()
                               for _ in range(self.__config.num_honest)]
        self.__all_nodes += self.__honest_nodes

    def run_experiment(self, progress_bar: bool = True) -> None:
        """a basic experiment with 10 nodes mining together at a rate of 1 block per second"""
        if progress_bar:
            self.setup_progress_bar()

        if self.__config.induce_split is not None:
            split_start, split_end = self.__config.induce_split
            if split_start < self.__run_time and split_end > split_start:
                self.__env.run(until=split_start)
                mid = len(self.__all_nodes)//2
                self.__network.induce_split(set(self.__all_nodes[:mid]))
            if split_end < self.__run_time:
                self.__env.run(until=split_end)
                self.__network.end_split()

        self.__env.run(until=self.__run_time)

        if self.__config.plot is not None:
            assert self.__download_log is not None
            plot_timeline(
                start_time=self.__config.plot[0], end_time=self.__config.plot[1],
                num_nodes=len(self.__all_nodes), download_log=self.__download_log)

    def setup_progress_bar(self, num_updates: int = 100) -> None:
        def progress_bar_process() -> Generator[simpy.events.Event, None, None]:
            with tqdm.tqdm(total=self.__run_time, disable=None, unit="sim_secs") as pbar:
                for i in range(num_updates):
                    yield self.__env.timeout(self.__run_time/num_updates)
                    pbar.update(self.__run_time/num_updates)
        self.__env.process(progress_bar_process())

    def get_results(self) -> Dict[str, Any]:
        honest_chain_height = self.calc_honest_chain_height()

        result: Dict[str, Any] = {}
        result["config"] = dataclasses.asdict(self.__config)
        result["honest_chain_height"] = honest_chain_height
        result["honest_chain_common_ancestor_height"] = self.get_common_ancestor_height()
        return result

    def calc_honest_chain_height(self) -> int:
        return max([node.mining_target.height for node in self.__honest_nodes])

    def get_common_ancestor_height(self) -> int:
        ancestor = self.__honest_nodes[0].mining_target
        for node in self.__honest_nodes:
            block = node.mining_target
            if ancestor.height > block.height:
                ancestor, block = block, ancestor
            while ancestor.height < block.height:
                assert block.parent is not None
                block = block.parent
            while ancestor != block:
                assert block.parent is not None
                block = block.parent
                assert ancestor.parent is not None
                ancestor = ancestor.parent
        return ancestor.height


def plot_timeline(start_time: float, end_time: float, num_nodes: int, download_log: Dict[Node, List[Tuple[Block, float, float]]]) -> None:
    import plotly.graph_objects as go  # type: ignore
    import plotly.express as px  # type: ignore

    fig = go.Figure()

    width = 0.1
    height = 0.25

    colors = px.colors.qualitative.Alphabet

    # plot download rectangles
    print("adding dl rectangles")
    for node in download_log:
        print("adding_shapes for node", node)
        dl_list = download_log[node]
        for block, start, end in dl_list:
            if start > end_time:
                continue
            if end < start_time:
                continue
            fig.add_shape(type="rect", xref="x", yref="y", x0=start, x1=end,
                          y0=node.id-height/2, y1=node.id + height/2,
                          fillcolor=colors[hash(block) % len(colors)], line=dict(color="black", width=1), opacity=0.2, layer="below")
            fig.add_annotation(
                x=(start+end)/2, y=node.id - height, xref='x', yref='y', text=str(block.id), opacity=0.3,
                showarrow=False)

    # plotting of blocks using markers
    print("drawing block markers")
    x_vals = [block.creation_time for block in Block.all_blocks if start_time <=
              block.creation_time <= end_time]
    y_vals = [block.miner.id if block.miner else 0 for block in Block.all_blocks if start_time <=
              block.creation_time <= end_time]
    text = [str(block.id) for block in Block.all_blocks if start_time <=
            block.creation_time <= end_time]
    fig.add_trace(go.Scatter(mode="markers+text", x=x_vals, y=y_vals, text=text, textposition="top center", marker_symbol="square",
                             marker_line_color="midnightblue", marker_color="lightskyblue",
                             marker_line_width=2, marker_size=10))

    print("drawing block arrows")
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

    print("finalizing figure layout")
    # Set axes ranges
    fig.update_xaxes(
        range=[start_time - width, end_time + width], showgrid=False, zeroline=False)
    fig.update_yaxes(range=[0 - 3*height, num_nodes -
                     1 + 3*height], dtick=1, tick0=1, showgrid=False, zeroline=False,
                     tickvals=list(range(num_nodes)), ticktext=[f"Node {i}" for i in range(num_nodes)], tickmode="array")
    fig.update_layout(xaxis_title="time (sec)", width=800,
                      height=400)

    out_path = os.path.join(BASE_PATH, "images/")
    out_file = os.path.join(out_path, "block_trace.svg")
    out_file2 = os.path.join(out_path, "block_trace.png")

    print("Saving plot...")
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    fig.write_image(out_file)
    fig.write_image(out_file2)
