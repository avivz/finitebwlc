
from typing import List, Generator, TYPE_CHECKING
from block import Block
import simpy
if TYPE_CHECKING:
    import node


class Network:
    def __init__(self, header_delay: float, env: simpy.core.Environment) -> None:
        self.__header_delay = header_delay
        self.__nodes: List[node.Node] = []
        self.__env = env

    def connect(self, node: "node.Node") -> None:
        self.__nodes.append(node)

    def notify_all_of_header(self, sender: "node.Node", block: Block) -> None:
        for node in self.__nodes:
            if node is not sender:
                self.__env.process(self._send_block_to_node(block, node))

    def _send_block_to_node(self, block: Block, node: "node.Node") -> Generator[simpy.events.Timeout, None, None]:
        yield self.__env.timeout(self.__header_delay)
        node.receive_header(block)
