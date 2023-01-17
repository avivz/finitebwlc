
from typing import List, Generator, TYPE_CHECKING, Dict, Tuple, Optional, Set
from .block import Block
import simpy.events
import simpy.core
import simpy.exceptions
if TYPE_CHECKING:
    from .node import Node


class Network:
    def __init__(self, env: simpy.core.Environment, download_log: Optional[Dict["Node", List[Tuple[Block, float, float]]]]) -> None:
        self.__nodes: List[Node] = []
        self.__download_log = download_log
        self.__env = env
        self.__split: List[Node] = []
        self.__split2: List[Node] = []

    def connect(self, node: "Node") -> None:
        self.__nodes.append(node)
        if self.__download_log is not None:
            self.__download_log[node] = []

    def induce_split(self, split: Set["Node"]) -> None:
        self.__split = list(split)
        self.__split2 = list(
            node for node in self.__nodes if node not in split)

    def end_split(self) -> None:
        self.__split = []
        self.__split2 = []

    def schedule_notify_all_of_header(self, sender: "Node", block: Block) -> None:
        nodes_to_notify = self.__nodes
        if self.__split:
            if sender in self.__split:
                nodes_to_notify = self.__split
            else:
                nodes_to_notify = self.__split2

        for node in nodes_to_notify:
            if node is not sender:
                def task(node: "Node", block: Block) -> Generator[simpy.events.Event, None, None]:
                    yield self.__env.timeout(node.header_delay)
                    node.receive_header(block)
                self.__env.process(task(node, block))

    def schedule_download_single_block(self, downloader: "Node", block: Block, bandwidth: float,
                                       fraction_already_dled: float) -> simpy.events.Process:
        if not block.is_available:
            raise ValueError(f"block is not available! {block}")

        def download_task() -> Generator[simpy.events.Event, None, None]:
            if bandwidth <= 0:
                time_to_download = 0.0
            else:
                time_to_download = (1-fraction_already_dled)/bandwidth
            start_time = self.__env.now
            try:
                yield self.__env.timeout(time_to_download)
                downloader.download_complete(block)
            except simpy.exceptions.Interrupt as i:
                elapsed_time = self.__env.now - start_time
                fraction_downloaded = elapsed_time*bandwidth + fraction_already_dled
                downloader.download_interrupted(block, fraction_downloaded)
            finally:
                if self.__download_log:
                    end_time = self.__env.now
                    self.__download_log[downloader].append(
                        (block, float(start_time), float(end_time)))

        return self.__env.process(download_task())

    @property
    def download_log(self) -> Optional[Dict["Node", List[Tuple[Block, float, float]]]]:
        return self.__download_log
