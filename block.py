from typing import List, Iterator, Optional, ClassVar
import uuid


class Block:
    __next_id: ClassVar[int] = 0

    def __init__(self, parent: Optional["Block"]):
        self.__id = Block.__next_id
        Block.__next_id += 1
        self.__parent = parent
        self.__children: List["Block"] = []
        if parent:
            parent.__children.append(self)
            self.__height: int = parent.__height+1
        else:
            self.__height = 0

    @property
    def height(self) -> int:
        return self.__height

    @property
    def parent(self) -> Optional["Block"]:
        return self.__parent

    def children_iter(self) -> Iterator["Block"]:
        yield from self.__children

    def __hash__(self) -> int:
        return self.__id
