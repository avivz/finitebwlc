
from .block import Block
from .node import Node
import sim.network as network


class DumbAttacker(Node):
    def __init__(self, node_id: str, genesis: Block, mining_rate: float, network: network.Network) -> None:
        super().__init__(node_id, genesis, mining_rate, network=network)
        self._tip = genesis

    def mine_block(self) -> Block:
        block = super().mine_block()

        self._broadcast_header(block)
        self._mining_target = block
        self._tip = block
        return block

    def receive_header(self, block: Block) -> None:
        super().receive_header(block)
        self._mining_target = self._tip

    def download_complete(self, block: Block) -> None:
        super().download_complete(block)
        self._mining_target = self._tip

    def download_interrupted(self, block: Block, fraction_downloaded: float) -> None:
        super().download_interrupted(block, fraction_downloaded)
        self._mining_target = self._tip
