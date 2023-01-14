from typing import TypeVar, Generic, List, Tuple

ITEM_TYPE = TypeVar('ITEM_TYPE')
PRIO_TYPE = TypeVar('PRIO_TYPE')


class LimittedQueue(Generic[ITEM_TYPE, PRIO_TYPE]):
    """max priority queue that keeps only the top k items. 
    Enqueue is O(n) where n is the actual queue size, dequeue is O(1)
    If two equal priority items are placed inside the queue, the earlier one has higher priority"""

    def __init__(self, buffer_size: int = 10) -> None:
        # a list of recent items entered to the queue:
        self._queue: List[Tuple[PRIO_TYPE, ITEM_TYPE]] = list()
        self._buffer_size = buffer_size

    def enqueue(self, item: ITEM_TYPE, priority: PRIO_TYPE) -> None:
        rec = priority, item
        if len(self._queue) >= self._buffer_size:
            for ind in range(len(self._queue)-1, -1, -1):
                if self._queue[ind][0] < rec[0]:  # type: ignore
                    rec, self._queue[ind] = self._queue[ind], rec
        else:
            self._queue.append(rec)
            ind = len(self._queue)-2

            while ind > -1 and \
                    self._queue[ind][0] >= self._queue[ind+1][0]:  # type: ignore
                self._queue[ind], self._queue[ind +
                                              1] = self._queue[ind+1], self._queue[ind]
                ind -= 1

    def dequeue(self) -> ITEM_TYPE:
        _, result = self._queue.pop()
        return result

    def peek(self) -> ITEM_TYPE:
        return self._queue[-1][1]

    def __len__(self) -> int:
        return len(self._queue)
