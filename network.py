
from typing import List, Generator, TYPE_CHECKING
from block import Block
import simpy.events
import simpy.core
import simpy.exceptions
if TYPE_CHECKING:
    from node import Node


class Network:
    def __init__(self, header_delay: float, env: simpy.core.Environment) -> None:
        self.__header_delay = header_delay
        self.__nodes: List[Node] = []
        self.__env = env

    def connect(self, node: "Node") -> None:
        self.__nodes.append(node)

    def schedule_notify_all_of_header(self, sender: "Node", block: Block) -> None:
        for node in self.__nodes:
            if node is not sender:
                def task(node: "Node", block: Block) -> Generator[simpy.events.Event, None, None]:
                    yield self.__env.timeout(self.__header_delay)
                    node.receive_header(block)
                self.__env.process(task(node, block))

    # def _send_block_to_node(self, block: Block, node: "Node") -> Generator[simpy.events.Event, None, None]:
    #     yield self.__env.timeout(self.__header_delay)
    #     node.receive_header(block)

    def schedule_download_single_block(self, downloader: "Node", block: Block, bandwidth: float) -> simpy.events.Process:

        def download_task() -> Generator[simpy.events.Event, None, None]:
            time_to_download = 1/bandwidth
            start_time = self.__env.now
            try:
                yield self.__env.timeout(time_to_download)
                downloader.progressed_downloading(block, 1.0)
            except simpy.exceptions.Interrupt as i:
                elapsed_time = self.__env.now - start_time
                fraction_downloaded = elapsed_time*bandwidth
                downloader.progressed_downloading(block, fraction_downloaded)

        return self.__env.process(download_task())
