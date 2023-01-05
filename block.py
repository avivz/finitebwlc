from typing import List, Iterator


class Block:
    def __init__(self, parent: "Block"):
        self.__parent = parent
        self.__children: List["Block"] = []
        self.__height: int = 0 if parent is None else parent.__height+1
        self.__parent.__children.append(self)

    @property
    def height(self) -> int:
        return self.__height

    @property
    def parent(self) -> "Block":
        return self.__parent

    def children_iter(self) -> Iterator["Block"]:
        yield from self.__children
