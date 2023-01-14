from typing import TypeVar, Generic, List, Tuple, Any

T = TypeVar('T')


class LimittedQueue(Generic[T]):
    """max priority queue that keeps only the top k items. 
    Enqueue is O(n) where n is the actual queue size, dequeue is O(1)"""

    def __init__(self, buffer_size: int = 10) -> None:
        # a list of recent items entered to the queue:
        self._queue: List[Tuple[Any, T]] = list()
        self._buffer_size = buffer_size

    def enqueue(self, item: T, priority: Any) -> None:
        rec = priority, item
        if len(self._queue) >= self._buffer_size:
            for ind in range(len(self._queue)-1, -1, -1):
                if self._queue[ind][0] < rec[0]:
                    rec, self._queue[ind] = self._queue[ind], rec
        else:
            self._queue.append(rec)
            ind = len(self._queue)-2
            while ind > -1:
                if self._queue[ind] > self._queue[ind+1]:
                    self._queue[ind], self._queue[ind +
                                                  1] = self._queue[ind+1], self._queue[ind]
                ind -= 1

    def dequeue(self) -> T:
        _, result = self._queue.pop()
        return result

    def peek(self) -> T:
        return self._queue[-1][1]

    def __len__(self) -> int:
        return len(self._queue)
