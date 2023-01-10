
from typing import Set, ClassVar, Optional
from block import Block
import network
import simpy.events


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
        self.__longest_header_tip: Optional[Block] = None
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
        print(
            f"Mining: Node {self} mines block {block}")

        self.__downloaded_blocks.add(block)
        self.__longest_downloaded_chain = block

        if not self.__longest_header_tip or self.__longest_header_tip.height <= block.height:
            self.__longest_header_tip = block

        self.__network.schedule_notify_all_of_header(self, block)
        self._reconsider_next_download()

    def receive_header(self, block: Block) -> None:
        print(f"Header: Node {self} learns of header {block}")
        if not self.__longest_header_tip or self.__longest_header_tip.height < block.height:
            self.__longest_header_tip = block

        # reconsider what to download
        self._reconsider_next_download()

    def _reconsider_next_download(self) -> None:
        # find the preferred download target:
        preferred_download = self._find_preferred_download_target()

        # if this is a new target, interrupt the old download.
        if self.__download_target != preferred_download:
            # interrupt the old process if it exists
            if self.__download_process:
                self.__download_process.interrupt()

            self.__download_target = preferred_download
            # schedule a new download.
            if preferred_download is not None:
                self.__download_process = self.__network.schedule_download_single_block(
                    self, preferred_download, self.bandwidth)

    # TODO: this is where the behavior of nodes changes the download rule!
    def _find_preferred_download_target(self) -> Optional[Block]:
        if self.__longest_header_tip is None or self.__longest_header_tip in self.__downloaded_blocks:
            return None
        cur = self.__longest_header_tip
        # travel back to a block that has a downloaded parent
        while cur.parent and cur.parent not in self.__downloaded_blocks:
            cur = cur.parent
        return cur

    def __hash__(self) -> int:
        return self.__id

    def progressed_downloading(self, block: Block, fraction_downloaded: float) -> None:
        # precision for comparissons. blocks are considered complete if this is the fraction missing.
        EPS = 0.000001

        # finish off the current download process.
        self.__download_process = None
        self.__download_target = None

        print(f"Block: Node {self} downloaded block {block}")
        # add block to download store:
        if abs(fraction_downloaded - 1.0) <= EPS:
            self.__downloaded_blocks.add(block)
            if not self.__longest_downloaded_chain or block.height > self.__longest_downloaded_chain.height:
                self.__longest_downloaded_chain = block
            self._reconsider_next_download()
        else:
            # TODO handle partial downloads here. Currently partial downloads are discarded.
            # we don't start a new download here because we assume an interrupt means one was already scheduled
            # this needs to be fixed if block downloads are resumed,because then a fraction can also be a completion.
            pass
