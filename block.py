from typing import List, Iterator, Optional


class Block:
    __slots__ = ['__parent', '__children', '__height',
                 'height', 'parent', 'children_iter']

    def __init__(self, parent: Optional["Block"]):
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
