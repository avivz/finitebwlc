
from .block import Block
from .node import Node
import sim.network as network


class SPVNode(Node):
    def __init__(self, genesis: Block, mining_rate: float, bandwidth: float,
                 header_delay: float, network: network.Network) -> None:
        super().__init__(genesis, mining_rate, bandwidth, header_delay, network)

    def mine_block(self) -> Block:
        block = super().mine_block()

        self._broadcast_header(block)
        return block

    def receive_header(self, block: Block) -> None:
        super().receive_header(block)
        self.download_complete(block)

    def download_complete(self, block: Block) -> None:
        super().download_complete(block)