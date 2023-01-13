from typing import TypeVar, Generic, List, Dict, Tuple, Any, Optional

T = TypeVar('T')


class OptimisticQueue(Generic[T]):
    """ assumes items have a unique priority. If an item is inserted twice, the last priority is saved only."""

    def __init__(self, buffer_size: int = 5) -> None:

        # a list of recent items entered to the queue:
        self._recent: List[Tuple[Any, T]] = list()

        # all other items (not in buffer) inserted mapped to priority:
        self._all_others: Dict[T, Any] = dict()

        self._size = 0

        self._max_buffer_size = buffer_size

        self._max_priority_item_outside_buffer: Optional[T] = None

    def enqueue(self, priority: Any, item: T) -> None:
        ind = self.__find_ind_in_recent(item)
        if ind > -1:
            self._recent[ind] = (priority, item)
            return

        if item in self._all_others:
            del self._all_others[item]
            self._size -= 1

        self._recent.append((priority, item))
        self._size += 1

        self._evict_from_buffer()

    def _evict_from_buffer(self) -> None:
        """evict from the buffer if it is too large"""
        if len(self._recent) <= self._max_buffer_size:
            return
        prio, item = self._recent[0]
        del self._recent[0]

        self._all_others[item] = prio
        if self._max_priority_item_outside_buffer is None or self._all_others[self._max_priority_item_outside_buffer] < prio:
            self._max_priority_item_outside_buffer = item

    def __find_ind_in_recent(self, item: T) -> int:
        ind = -1
        for i, record in enumerate(self._recent):
            if record[1] == item:
                ind = i
                break
        return ind

    def _find_max_priority_item(self) -> Tuple[T, int]:
        """returns item and its location in the buffer (or -1 if not in buffer)"""
        max_ind = -1
        for i, rec in enumerate(self._recent):
            if self._recent[max_ind][0] < rec[0]:
                max_ind = i

        if max_ind > -1 and self._max_priority_item_outside_buffer is not None \
                and self._recent[max_ind][0] > self._all_others[self._max_priority_item_outside_buffer]:
            return self._recent[max_ind][1], max_ind

        assert self._max_priority_item_outside_buffer is not None
        return self._max_priority_item_outside_buffer, -1

    def dequeue(self) -> T:
        if not self._size:
            raise LookupError("Dequeue from Empty Queue")
        self._size -= 1

        item, ind = self._find_max_priority_item()

        if ind == -1:
            del self._all_others[item]

            new_max_item: Optional[T] = None
            new_max_prio: Any = None
            for temp_prio, temp_item in self._all_others.values():
                if new_max_prio is None or new_max_prio < temp_prio:
                    new_max_prio = temp_prio
                    new_max_item = temp_item
            self._max_priority_item_outside_buffer = new_max_item
        else:
            del self._recent[ind]

        return item

    def peek(self) -> T:
        item, ind = self._find_max_priority_item()
        return item

    def __len__(self) -> int:
        return self._size
