
from abc import ABC
from typing import Set, ClassVar, Optional
from .block import Block
import src.network as network
import simpy.events
import src.simulation_parameters as simulation_parameters
import logging
import pylru  # type: ignore


class Node(ABC):
    __next_id: ClassVar[int] = 0

    def __init__(self, mining_rate: float, bandwidth: float, header_delay: float,
                 network: network.Network, partial_block_cache_size: int = 10) -> None:
        # set a unique id:
        self.__id = Node.__next_id
        Node.__next_id += 1
        self.__hash = hash(self.__id)
        self.__description = f"{self.__class__.__name__}_{self.id}"

        self.__mining_rate = mining_rate
        self.__bandwidth = bandwidth
        self.__header_delay = header_delay

        # connect to the network
        network.connect(self)
        self.__network = network

        # mining target:
        self._mining_target = simulation_parameters.GENESIS

        # download management:
        self.__download_process: Optional[simpy.events.Process] = None
        self.__download_target: Optional[Block] = None
        self._downloaded_blocks: Set[Block] = {simulation_parameters.GENESIS}

        self._partial_blocks = pylru.lrucache(partial_block_cache_size)

    @property
    def mining_rate(self) -> float:
        return self.__mining_rate

    @property
    def id(self) -> int:
        return self.__id

    @property
    def bandwidth(self) -> float:
        return self.__bandwidth

    @property
    def header_delay(self) -> float:
        return self.__header_delay

    def __str__(self) -> str:
        return self.__description

    def mine_block(self) -> Block:
        """This method is called externally by the mining oracle.
        the block is mined on top of the current mining target, and the mining target is adjusted to the new block"""
        block = Block(self, self._mining_target,
                      simulation_parameters.ENV.now)
        message = f"Mining t={simulation_parameters.ENV.now:.2f}: Node {self} mines block {block}"
        logging.getLogger("SIM_INFO").info(message)

        self._downloaded_blocks.add(block)
        self._mining_target = block
        return block

    def receive_header(self, block: Block) -> None:
        message = f"Header t={simulation_parameters.ENV.now:.2f}: Node {self} learns of header {block}"
        logging.getLogger("SIM_INFO").info(message)

    def _broadcast_header(self, block: Block) -> None:
        self.__network.schedule_notify_all_of_header(self, block)

    def _stop_cur_download_and_start_new_one(self, block: Optional[Block]) -> None:
        """This methods interrupts any current download and starts a new block download."""
        # if this is the same target, do nothing (keep downloading it)
        if self.__download_target == block:
            return

        # interrupt the old process if it exists
        if self.__download_process:
            self.__download_process.interrupt()
            self.__download_process = None

        self.__download_target = block
        # schedule a new download.
        if block is not None:
            fraction_already_dled = 0
            if block in self._partial_blocks:
                fraction_already_dled = self._partial_blocks[block]
            self.__download_process = self.__network.schedule_download_single_block(
                self, block, self.bandwidth, fraction_already_dled)

    def __hash__(self) -> int:
        return self.__hash

    def download_complete(self, block: Block) -> None:
        """Method that is called when dowloading a block is finished. The mining target is re-adjusted if the current downloaded chain is longest"""
        # finish off the current download process.
        self.__download_process = None
        self.__download_target = None

        message = f"Download Complete t={simulation_parameters.ENV.now:.2f}: Node {self} downloaded block {block}"
        logging.getLogger("SIM_INFO").info(message)

        # add block to download store:
        self._downloaded_blocks.add(block)
        if block in self._partial_blocks:
            del self._partial_blocks[block]

        if block.height > self._mining_target.height:
            self._mining_target = block

    def download_interrupted(self, block: Block, cummulative_fraction_downloaded: float) -> None:
        message = f"Download Interrupt t={simulation_parameters.ENV.now:.2f}: Node {self} downloaded block {block}, fraction: {cummulative_fraction_downloaded}"
        logging.getLogger("SIM_INFO").info(message)

        self._partial_blocks[block] = cummulative_fraction_downloaded
        # TODO handle partial downloads here. Currently partial downloads are discarded.

    def push_download(self, block: Block) -> None:
        message = f"Force-download t={simulation_parameters.ENV.now:.2f}: Node {self} force-downloaded block {block}"
        logging.getLogger("SIM_INFO").info(message)

        cur = block
        while cur.parent and cur.parent not in self._downloaded_blocks:
            cur = cur.parent
            self._downloaded_blocks.add(cur)
            if cur in self._partial_blocks:
                del self._partial_blocks[cur]
        self.download_complete(block)
