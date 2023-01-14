from typing import List, Iterator, Optional, ClassVar, TYPE_CHECKING
if TYPE_CHECKING:
    from node import Node


class Block:
    all_blocks: ClassVar[List["Block"]] = []
    blocks_by_height: ClassVar[List[int]] = []

    def __init__(self, miner: Optional["Node"], parent: Optional["Block"], creation_time: float):
        Block.all_blocks.append(self)

        self.__parent = parent
        self.__children: List["Block"] = []
        self.__is_available = True
        self.__creation_time = creation_time
        self.__miner = miner
        if parent:
            parent.__children.append(self)
            self.__height: int = parent.__height+1
        else:
            self.__height = 0

        if self.__height >= len(Block.blocks_by_height):
            Block.blocks_by_height.append(1)
        else:
            Block.blocks_by_height[self.__height] += 1

        self.__id = f"{self.__height}.{Block.blocks_by_height[self.__height]}"
        self.__hash = hash(self.__id)

        self.__description = f"Block(id={self.id}, h={self.height}, parent_id={self.parent.id if self.parent else None}, creation_time={self.__creation_time})"

    @property
    def creation_time(self) -> float:
        return self.__creation_time

    @property
    def miner(self) -> Optional["Node"]:
        return self.__miner

    @property
    def is_available(self) -> bool:
        return self.__is_available

    @is_available.setter
    def is_available(self, available: bool) -> None:
        self.__is_available = available

    @property
    def height(self) -> int:
        return self.__height

    @property
    def parent(self) -> Optional["Block"]:
        return self.__parent

    @property
    def id(self) -> str:
        return self.__id

    def children_iter(self) -> Iterator["Block"]:
        yield from self.__children

    def __hash__(self) -> int:
        return self.__hash

    def __str__(self) -> str:
        return self.__description
