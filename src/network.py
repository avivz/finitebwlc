
from typing import List, Generator, TYPE_CHECKING, Dict, Tuple, Optional
from block import Block
import simpy.events
import simpy.core
import simpy.exceptions
import simulation_parameters
if TYPE_CHECKING:
    from node import Node


class Network:
    def __init__(self, download_log: Optional[Dict["Node", List[Tuple[Block, float, float]]]]) -> None:
        self.__nodes: List[Node] = []
        self.__download_log = download_log

    def connect(self, node: "Node") -> None:
        self.__nodes.append(node)
        if self.__download_log is not None:
            self.__download_log[node] = []

    def schedule_notify_all_of_header(self, sender: "Node", block: Block) -> None:
        for node in self.__nodes:
            if node is not sender:
                def task(node: "Node", block: Block) -> Generator[simpy.events.Event, None, None]:
                    yield simulation_parameters.ENV.timeout(node.header_delay)
                    node.receive_header(block)
                simulation_parameters.ENV.process(task(node, block))

    # def _send_block_to_node(self, block: Block, node: "Node") -> Generator[simpy.events.Event, None, None]:
    #     yield self.__env.timeout(self.__header_delay)
    #     node.receive_header(block)

    def schedule_download_single_block(self, downloader: "Node", block: Block, bandwidth: float,
                                       fraction_already_dled: float) -> simpy.events.Process:
        if not block.is_available:
            raise ValueError(f"block is not available! {block}")

        def download_task() -> Generator[simpy.events.Event, None, None]:
            if bandwidth <= 0:
                time_to_download = 0.0
            else:
                time_to_download = (1-fraction_already_dled)/bandwidth
            start_time = simulation_parameters.ENV.now
            try:
                yield simulation_parameters.ENV.timeout(time_to_download)
                downloader.download_complete(block)
            except simpy.exceptions.Interrupt as i:
                elapsed_time = simulation_parameters.ENV.now - start_time
                fraction_downloaded = elapsed_time*bandwidth + fraction_already_dled
                downloader.download_interrupted(block, fraction_downloaded)
            finally:
                if self.__download_log:
                    end_time = simulation_parameters.ENV.now
                    self.__download_log[downloader].append(
                        (block, float(start_time), float(end_time)))

        return simulation_parameters.ENV.process(download_task())

    def push_block(self, nodes: List["Node"], block: Block) -> None:
        for node in nodes:
            node.push_download(block)

    @property
    def download_log(self) -> Optional[Dict["Node", List[Tuple[Block, float, float]]]]:
        return self.__download_log
