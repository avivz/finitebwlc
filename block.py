from typing import List


class Block:
    def __init__(self, parent: "Block"):
        self.__parent = parent
        self.__children: List["Block"] = []
        self.__height: int = 0 if parent is None else parent.__height+1

    @property
    def height(self) -> int:
        return self.__height

    @property
    def parent(self) -> "Block":
        return self.__parent
