
from typing import List, Generator, TYPE_CHECKING
from block import Block
import simpy.events
import simpy.core
import simpy.exceptions
import simulation_parameters
if TYPE_CHECKING:
    from node import Node


class Network:
    def __init__(self, f_same_group) -> None:
        self.__nodes: List[Node] = []
        self.__f_same_group = f_same_group

    def connect(self, node: "Node") -> None:
        self.__nodes.append(node)

    def schedule_notify_all_of_header(self, sender: "Node", block: Block) -> None:
        for node in self.__nodes:
            if node is not sender:
                def task(node: "Node", block: Block) -> Generator[simpy.events.Event, None, None]:
                    yield simulation_parameters.ENV.timeout(node.header_delay)
                    node.receive_header(block)
                    if self.__f_same_group(node, sender):
                        node.push_download(block)

                simulation_parameters.ENV.process(task(node, block))

    def schedule_download_single_block(self, downloader: "Node", block: Block, bandwidth: float) -> simpy.events.Process:
        if not block.is_available:
            raise ValueError(f"block is not available! {block}")

        def download_task() -> Generator[simpy.events.Event, None, None]:
            time_to_download = 1/bandwidth
            start_time = simulation_parameters.ENV.now
            try:
                yield simulation_parameters.ENV.timeout(time_to_download)
                downloader.progressed_downloading(block, 1.0)
            except simpy.exceptions.Interrupt as i:
                elapsed_time = simulation_parameters.ENV.now - start_time
                fraction_downloaded = elapsed_time*bandwidth
                downloader.progressed_downloading(block, fraction_downloaded)

        return simulation_parameters.ENV.process(download_task())
