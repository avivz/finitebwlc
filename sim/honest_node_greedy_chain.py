
from typing import Optional
from .block import Block
from .node import Node
import sim.network as network
from typing import Dict


class HonestNodeGreedy(Node):
    def __init__(self, genesis: Block, mining_rate: float, bandwidth: float,
                 header_delay: float, network: network.Network, buffer_size: int = 100) -> None:
        super().__init__(genesis, mining_rate, bandwidth, header_delay, network)
        self.__tip_to_candidate: Dict[Block, Block] = {}
        self.__buffer_size = buffer_size

    def mine_block(self) -> Block:
        block = super().mine_block()

        self._broadcast_header(block)
        self._reconsider_next_download()
        return block

    def receive_header(self, tip: Block) -> None:
        super().receive_header(tip)
        if tip in self._downloaded_blocks:
            return
        if tip in self.__tip_to_candidate:
            return
        candidate: Optional[Block] = None
        if tip.parent in self.__tip_to_candidate:
            # we delete the parent from the tip mapping, but not before we try to use it to find our way back to the downloaded chain to get our correct candidate
            potential_candidate = self.__tip_to_candidate[tip.parent]
            del self.__tip_to_candidate[tip.parent]
            if potential_candidate not in self._downloaded_blocks:
                candidate = potential_candidate
        if candidate is None:
            candidate = self._get_candidate(tip)
        self.__tip_to_candidate[tip] = candidate

        self._evict_if_needed()
        self._reconsider_next_download()

    def _evict_if_needed(self) -> None:
        if len(self.__tip_to_candidate) <= self.__buffer_size:
            return

        worst_tip = next(iter(self.__tip_to_candidate.keys()))
        worst_candidate_height = self.__tip_to_candidate[worst_tip].height
        for tip, candidate in self.__tip_to_candidate.items():
            if candidate.height < worst_candidate_height or candidate.height == worst_candidate_height and tip.height < worst_tip.height:
                worst_tip = tip
                worst_candidate_height = candidate.height
        del self.__tip_to_candidate[worst_tip]

    def _get_candidate(self, tip: Block) -> Block:
        cur = tip
        while cur.parent not in self._downloaded_blocks:
            assert cur.parent is not None, "parent of cur was found to be none!"
            cur = cur.parent
        return cur

    def _reconsider_next_download(self) -> None:
        # find the preferred download target:
        preferred_download = self._find_preferred_download_target()
        self._stop_cur_download_and_start_new_one(preferred_download)

    def _find_preferred_download_target(self) -> Optional[Block]:
        best_candidate: Optional[Block] = None
        best_candidate_tip_height = 0

        for tip, candidate in list(self.__tip_to_candidate.items()):
            if candidate in self._downloaded_blocks:
                new_candidate = self._get_candidate(tip)
                del self.__tip_to_candidate[tip]
                if new_candidate is None:
                    continue
                candidate = new_candidate
                self.__tip_to_candidate[tip] = new_candidate
            if not candidate.is_available:
                del self.__tip_to_candidate[tip]

            if best_candidate is None or \
                    best_candidate.height < candidate.height or \
                    best_candidate.height == candidate.height and tip.height > best_candidate_tip_height:
                best_candidate = candidate
                best_candidate_tip_height = tip.height
        return best_candidate

    def download_complete(self, block: Block) -> None:
        super().download_complete(block)
        for tip, candidate in list(self.__tip_to_candidate.items()):
            if candidate == block:
                if tip != block:
                    assert tip not in self._downloaded_blocks, "tip found in downloaded blocks"
                    new_candidate = self._get_candidate(block)
                    self.__tip_to_candidate[tip] = new_candidate
                else:
                    del self.__tip_to_candidate[tip]
        self._reconsider_next_download()

    def download_interrupted(self, block: Block, fraction_downloaded: float) -> None:
        return super().download_interrupted(block, fraction_downloaded)
