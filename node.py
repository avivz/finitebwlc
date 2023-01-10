
from typing import Set, ClassVar, Optional
from block import Block
import network
import simpy.events
from DataStructures.AbstractDataStructures import DuplicatePriorityQueue  # type: ignore
import simulation_parameters


class Node:
    __next_id: ClassVar[int] = 0

    def __init__(self, mining_rate: float, bandwidth: float, header_delay: float, network: network.Network) -> None:
        # set a unique id:
        self.__id = Node.__next_id
        Node.__next_id += 1

        self.__mining_rate = mining_rate
        self.__bandwidth = bandwidth
        self.__header_delay = header_delay

        self.__downloaded_blocks: Set[Block] = set()

        # connect to the network
        network.connect(self)
        self.__network = network

        # download management:
        self.__download_process: Optional[simpy.events.Process] = None
        self.__download_target: Optional[Block] = None

        # honest node behavior:
        self.__download_pq: DuplicatePriorityQueue = DuplicatePriorityQueue()
        self.__longest_downloaded_chain: Optional[Block] = None

    @property
    def mining_rate(self) -> float:
        return self.__mining_rate

    @property
    def id(self) -> float:
        return self.__id

    @property
    def bandwidth(self) -> float:
        return self.__bandwidth

    @property
    def header_delay(self) -> float:
        return self.__header_delay

    def __str__(self) -> str:
        return f"Node_{self.id}"

    def mine_block(self) -> None:
        """This method is called externally by the mining oracle."""
        block = Block(self.__longest_downloaded_chain)
        if simulation_parameters.verbose:
            print(f"Mining: Node {self} mines block {block}")

        self.__downloaded_blocks.add(block)
        self.__longest_downloaded_chain = block

        self.__network.schedule_notify_all_of_header(self, block)
        self._reconsider_next_download()

    def receive_header(self, block: Block) -> None:
        if simulation_parameters.verbose:
            print(f"Header: Node {self} learns of header {block}")
        if self.__download_pq.contains_element(block):
            return
        # TODO: The priority that is chosen here should be changed for other download rules
        self.__download_pq.enqueue(block, block.height)
        self._reconsider_next_download()

    def _reconsider_next_download(self) -> None:
        # find the preferred download target:
        preferred_download = self._find_preferred_download_target()

        # if this is the same target, do nothing (keep downloading it)
        if self.__download_target == preferred_download:
            return

        # interrupt the old process if it exists
        if self.__download_process:
            self.__download_process.interrupt()
            self.__download_process = None

        self.__download_target = preferred_download
        # schedule a new download.
        if preferred_download is not None:
            self.__download_process = self.__network.schedule_download_single_block(
                self, preferred_download, self.bandwidth)

    def _find_preferred_download_target(self) -> Optional[Block]:
        while self.__download_pq.size > 0:
            block = self.__download_pq.peek()
            if block in self.__downloaded_blocks:
                self.__download_pq.dequeue()
                continue

            cur: Block = block
            # travel back to a block that has a downloaded parent
            while cur.parent and cur.parent not in self.__downloaded_blocks:
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
        # precision for comparissons. blocks are considered complete if this is the fraction missing.
        EPS = 0.000001

        # finish off the current download process.
        self.__download_process = None
        self.__download_target = None

        if simulation_parameters.verbose:
            print(
                f"Download: Node {self} downloaded block {block}, fraction: {fraction_downloaded}")

        # add block to download store:
        if abs(fraction_downloaded - 1.0) <= EPS:
            self.__downloaded_blocks.add(block)
            if not self.__longest_downloaded_chain or block.height > self.__longest_downloaded_chain.height:
                self.__longest_downloaded_chain = block
            if block in self.__download_pq:
                self.__download_pq.remove_element(block)
            self._reconsider_next_download()
        else:
            # TODO handle partial downloads here. Currently partial downloads are discarded.
            # we don't start a new download here because we assume an interrupt means one was already scheduled
            # this needs to be fixed if block downloads are resumed,because then a fraction can also be a completion.
            pass
