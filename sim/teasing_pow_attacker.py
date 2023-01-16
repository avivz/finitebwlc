
from .block import Block
from .node import Node
import sim.network as network


class TeasingPoWAttacker(Node):
    """this attacker mines on its own chain. As it receives blocks from the network, 
    it always releases 2 headers ahead but allows download only one header ahead
    thus, a node that downloads towards the longest tip always first downloads the matching block of this attacker."""

    def __init__(self, genesis: Block, mining_rate: float, network: network.Network) -> None:
        super().__init__(genesis, mining_rate, bandwidth=0, header_delay=0, network=network)
        self._tip = genesis
        # this is the tip of the chain this node has allowed others to download.
        self._last_available = genesis

    def mine_block(self) -> Block:
        block = super().mine_block()
        block.is_available = False

        self._mining_target = block
        self._tip = block
        return block

    def receive_header(self, block: Block) -> None:
        super().receive_header(block)
        self._mining_target = self._tip

        while block.height-1 > self._last_available.height:
            children = self._last_available.get_children()
            if not children:
                return
            self._last_available = children[0]
            self._last_available.is_available = True

        if self._tip.height >= self._last_available.height+2:
            child = self._last_available.get_children()[0]
            grandson = child.get_children()[0]
            self._broadcast_header(grandson)

    def download_complete(self, block: Block) -> None:
        super().download_complete(block)
        self._mining_target = self._tip

    def download_interrupted(self, block: Block, fraction_downloaded: float) -> None:
        super().download_interrupted(block, fraction_downloaded)
        self._mining_target = self._tip
