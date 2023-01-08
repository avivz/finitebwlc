
from typing import Set, ClassVar, Optional, Generator
from block import Block
import network
import simpy.events


class Node:
    __next_id: ClassVar[int] = 0

    def __init__(self, mining_rate: float, bandwidth: float, network: network.Network) -> None:
        # set a unique id:
        self.__id = Node.__next_id
        Node.__next_id += 1

        self.__mining_rate = mining_rate
        self.__bandwidth = bandwidth

        self.__known_headers: Set[Block] = set()
        self.__downloaded_blocks: Set[Block] = set()

        # connect to the network
        self.__network = network
        self.__network.connect(self)

        # honest node behavior:
        self.__longest_header_tip: Optional[Block] = None
        self.__longest_downloaded_chain: Optional[Block] = None

    def receive_header(self, block: Block) -> None:
        print(f"Header: Node {self.id} learns of header {block.id}")

        self.__known_headers.add(block)
        if not self.__longest_header_tip or self.__longest_header_tip.height < block.height:
            self.__longest_header_tip = block

        # TODO fix this. blocks are downloaded in parallel w/ full bandwidth after initial delivery.
        if block not in self.__downloaded_blocks:
            self.__network.schedule_download_single_block(
                self, block, self.__bandwidth)

    def finished_downloading(self, block: Block) -> None:
        print(f"Block: Node {self.id} downloaded block {block.id}")
        self.__downloaded_blocks.add(block)
        if not self.__longest_downloaded_chain or block.height > self.__longest_downloaded_chain.height:
            self.__longest_downloaded_chain = block
        # TODO here I'd want to schedule other blocks, or readjust bandwidth

    def mine_block(self) -> None:
        """This method is called externally by the mining oracle."""
        block = Block(self.__longest_downloaded_chain)
        print(
            f"Mining: Node {self.id} mines block {block.id} of height {block.height}")

        self.__downloaded_blocks.add(block)
        self.__longest_downloaded_chain = block
        self.receive_header(block)
        self.__network.schedule_notify_all_of_header(self, block)

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
