
from typing import Set, ClassVar, Optional
from block import Block
import network
import simpy.events

EPS = 0.000001


class Node:
    __next_id: ClassVar[int] = 0

    def __init__(self, mining_rate: float, bandwidth: float, network: network.Network) -> None:
        # set a unique id:
        self.__id = Node.__next_id
        Node.__next_id += 1

        self.__mining_rate = mining_rate
        self.__bandwidth = bandwidth

        self.__downloaded_blocks: Set[Block] = set()

        # connect to the network
        network.connect(self)
        self.__network = network

        # download management:
        self.__download_process: Optional[simpy.events.Process] = None
        self.__download_target: Optional[Block] = None

        # honest node behavior:
        self.__longest_header_tip: Optional[Block] = None
        self.__longest_downloaded_chain: Optional[Block] = None

    def receive_header(self, block: Block) -> None:
        print(f"Header: Node {self} learns of header {block}")
        if not self.__longest_header_tip or self.__longest_header_tip.height < block.height:
            self.__longest_header_tip = block

        # reconsider what to download
        self._select_and_start_next_download()

    def progressed_downloading(self, block: Block, fraction_downloaded: float) -> None:
        # finish off the current download process.
        self.__download_process = None
        self.__download_target = None

        print(f"Block: Node {self} downloaded block {block}")
        # add block to download store:
        if abs(fraction_downloaded - 1.0) <= EPS:
            self.__downloaded_blocks.add(block)
            if not self.__longest_downloaded_chain or block.height > self.__longest_downloaded_chain.height:
                self.__longest_downloaded_chain = block
            self._select_and_start_next_download()
        else:
            # TODO handle partial downloads here. Currently partial downloads are discarded.
            # we don't start a new download here because we assume an interrupt means one was already scheduled
            # this needs to be fixed if block downloads are resumed,because then a fraction can also be a completion.
            pass

    def mine_block(self) -> None:
        """This method is called externally by the mining oracle."""
        block = Block(self.__longest_downloaded_chain)
        print(
            f"Mining: Node {self} mines block {block}")

        self.__downloaded_blocks.add(block)
        self.__longest_downloaded_chain = block

        if not self.__longest_header_tip or self.__longest_header_tip.height <= block.height:
            self.__longest_header_tip = block

        self.__network.schedule_notify_all_of_header(self, block)
        self._select_and_start_next_download()

    def _select_and_start_next_download(self) -> None:
        # if we already have the longest tip, no download target. Interrupt the current process if there is one.
        if self.__longest_header_tip is None or self.__longest_header_tip in self.__downloaded_blocks:
            self.__download_target = None
            if self.__download_process:
                self.__download_process.interrupt()
                self.__download_process = None
            return

        # otherwise, find the next block towards the longest header chain:
        cur = self.__longest_header_tip
        while cur.parent and cur.parent not in self.__downloaded_blocks:
            cur = cur.parent

        # if this is a new target, interrupt the old download and start a new one.
        if self.__download_target != cur:
            self.__download_target = cur
            if self.__download_process:
                self.__download_process.interrupt()
            self.__download_process = self.__network.schedule_download_single_block(
                self, cur, self.bandwidth)

    def __hash__(self) -> int:
        return self.__id

    @property
    def mining_rate(self) -> float:
        return self.__mining_rate

    @property
    def id(self) -> float:
        return self.__id

    @property
    def bandwidth(self) -> float:
        return self.__bandwidth

    def __str__(self) -> str:
        return f"Node_{self.id}"
