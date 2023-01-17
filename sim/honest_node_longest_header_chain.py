
from typing import Optional
from .block import Block
from .node import Node
import sim.network as network
from .limitted_queue import LimittedQueue


class HonestNodeLongestHeaderChain(Node):
    def __init__(self, genesis: Block, mining_rate: float, bandwidth: float,
                 header_delay: float, network: network.Network) -> None:
        super().__init__(genesis, mining_rate, bandwidth, header_delay, network)
        self.__dl_queue: LimittedQueue[Block,
                                       int] = LimittedQueue(buffer_size=100)

    def mine_block(self) -> Block:
        block = super().mine_block()

        self._broadcast_header(block)
        self._reconsider_next_download()
        return block

    def receive_header(self, block: Block) -> None:
        super().receive_header(block)
        self.__dl_queue.enqueue(block, block.height)
        self._reconsider_next_download()

    def _reconsider_next_download(self) -> None:
        # find the preferred download target:
        preferred_download = self._find_preferred_download_target()
        self._stop_cur_download_and_start_new_one(preferred_download)

    def _find_preferred_download_target(self) -> Optional[Block]:
        while len(self.__dl_queue) > 0:
            block = self.__dl_queue.peek()
            if block in self._downloaded_blocks:
                self.__dl_queue.dequeue()
                continue

            cur: Block = block
            # travel back to a block that has a downloaded parent
            while cur.parent and cur.parent not in self._downloaded_blocks:
                cur = cur.parent

            # if the block we want to download is discovered as unavailable, we remove the tip from further consideration (it needs to be re-anounced if it is to be considered again)
            if not cur.is_available:
                self.__dl_queue.dequeue()
                continue
            return cur
        return None

    def download_complete(self, block: Block) -> None:
        super().download_complete(block)
        self._reconsider_next_download()

    def download_interrupted(self, block: Block, fraction_downloaded: float) -> None:
        return super().download_interrupted(block, fraction_downloaded)
