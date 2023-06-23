
from .block import Block
from .node import Node
import sim.network as network
from typing import Optional


class TeasingPoWAttacker(Node):
    """this attacker mines on its own chain. As it receives blocks from the network, 
    it always releases 2 headers ahead but allows download only one header ahead
    thus, a node that downloads towards the longest tip always first downloads the matching block of this attacker."""

    def __init__(self, genesis: Block, mining_rate: float, network: network.Network) -> None:
        super().__init__(genesis, mining_rate, bandwidth=0, header_delay=0, network=network)

        # this is the tip of the chain this node is mining on:
        self._tip = genesis

        # this is the tip of the chain this node has allowed others to download.
        self._last_available = genesis

        # This is the next block that this node will release (if it has one) for others to download:
        self._next_available: Optional[Block] = None

    def mine_block(self) -> Block:
        block = super().mine_block()
        block.is_available = False

        if block.parent == self._last_available:
            self._next_available = block

        self._mining_target = block
        self._tip = block
        return block

    def receive_header(self, block: Block) -> None:
        super().receive_header(block)

        # Here the attacker will want to give up (if its tim is behind the honest chain):
        if block.height > self._tip.height:
            self._tip = block
            self._mining_target = block
            self._last_available = block
            self._next_available = None
            return

        self._mining_target = self._tip

        # make blocks available up to the height of the honest chain:
        while block.height-1 > self._last_available.height:

            if not self._next_available:
                return
            self._last_available = self._next_available
            self._last_available.is_available = True
            if self._next_available.get_children():
                self._next_available = self._next_available.get_children()[0]

        if self._next_available and self._next_available.get_children():
            self._broadcast_header(self._next_available.get_children()[0])

    def download_complete(self, block: Block) -> None:
        super().download_complete(block)
        self._mining_target = self._tip

    def download_interrupted(self, block: Block, fraction_downloaded: float) -> None:
        super().download_interrupted(block, fraction_downloaded)
        self._mining_target = self._tip
