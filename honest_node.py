
from typing import Optional
from block import Block
from node import Node
import network
from DataStructures.AbstractDataStructures import DuplicatePriorityQueue  # type: ignore


class HonestNode(Node):
    def __init__(self, mining_rate: float, bandwidth: float, header_delay: float, network: network.Network) -> None:
        super().__init__(mining_rate, bandwidth, header_delay, network)
        self.__download_pq: DuplicatePriorityQueue = DuplicatePriorityQueue()

    def mine_block(self) -> Block:
        block = super().mine_block()

        self._broadcast_header(block)
        self._reconsider_next_download()
        return block

    def receive_header(self, block: Block) -> None:
        super().receive_header(block)
        if self.__download_pq.contains_element(block):
            return
        # TODO: The priority that is chosen here should be changed for other download rules
        if self.__download_pq.contains_element(block.parent):
            self.__download_pq.remove_element(block.parent)
        self.__download_pq.enqueue(block, block.height)
        self._reconsider_next_download()

    def _reconsider_next_download(self) -> None:
        # find the preferred download target:
        preferred_download = self._find_preferred_download_target()
        self._stop_cur_download_and_start_new_one(preferred_download)

    def _find_preferred_download_target(self) -> Optional[Block]:
        while self.__download_pq.size > 0:
            block = self.__download_pq.peek()
            if block in self._downloaded_blocks:
                self.__download_pq.dequeue()
                continue

            cur: Block = block
            # travel back to a block that has a downloaded parent
            while cur.parent and cur.parent not in self._downloaded_blocks:
                cur = cur.parent

            # if the block we want to download is discovered as unavailable, we remove the tip from further consideration (it needs to be re-anounced if it is to be considered again)
            if not cur.is_available:
                self.__download_pq.dequeue()
                continue
            return cur
        return None

    def __hash__(self) -> int:
        return self.__id

    def progressed_downloading(self, block: Block, fraction_downloaded: float) -> None:
        super().progressed_downloading(block, fraction_downloaded)
        if abs(fraction_downloaded - 1.0) <= Node.DOWNLOAD_PRECISION:
            if block in self.__download_pq:
                self.__download_pq.remove_element(block)
            self._reconsider_next_download()
        else:
            # TODO handle partial downloads here.
            pass
