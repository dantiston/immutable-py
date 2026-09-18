#!/usr/bin/env python3

from typing import Callable, Generic, Iterable, Iterator, TypeVar, Union

from .collection import Indexed, ReturnT, ValueT, is_collection
from .equality import singleton


class List(Indexed[ValueT], Generic[ValueT]):
    def __init__(self, items: Iterable[ValueT] = ()) -> None:
        self.items = list(items)

    @classmethod
    def of(cls, *items: ValueT) -> "List":
        return List(items) if items else _empty_list

    @classmethod
    def is_list(cls, other) -> bool:
        return isinstance(other, List)

    def get(self, index: int, nsv: ValueT = singleton) -> ValueT:
        try:
            return self.items[index]
        except IndexError as e:
            if nsv is singleton:
                raise e
            return nsv

    def _normalize_index(self, index: int) -> int:
        return index + len(self.items) if index < 0 else index

    def set(self, index: int, value: ValueT) -> "List":
        index = self._normalize_index(index)
        if index < 0:
            return self
        items = self.items[:]
        if index >= len(items):
            items.extend([None] * (index - len(items) + 1))
        items[index] = value
        return List(items)

    def delete(self, index: int) -> "List":
        index = self._normalize_index(index)
        if not 0 <= index < len(self.items):
            return self
        items = self.items[:]
        items.pop(index)
        return List(items)

    remove = delete

    def insert(self, index: int, value: ValueT) -> "List":
        items = self.items[:]
        items.insert(index, value)
        return List(items)

    def push(self, *values: ValueT) -> "List":
        return List(self.items[:] + list(values))

    def pop(self) -> "List":
        if not self.items:
            return self
        return List(self.items[:-1])

    def unshift(self, *values: ValueT) -> "List":
        return List(list(values) + self.items[:])

    def shift(self) -> "List":
        return List(self.items[1:])

    def update(
        self,
        index: int,
        updater: Callable[[ValueT], ValueT],
        nsv: ValueT = singleton,
    ) -> "List":
        return self.set(index, updater(self.get(index, nsv)))

    def set_size(self, size: int) -> "List":
        if size < len(self.items):
            return List(self.items[:size])
        if size > len(self.items):
            return List(self.items[:] + [None] * (size - len(self.items)))
        return self

    def thru(self, updater: Callable[["List"], ReturnT]) -> ReturnT:
        return updater(self)

    def clear(self) -> "List":
        return _empty_list

    def concat(self, *values: Union[Iterable[ValueT], ValueT]) -> "List":
        if not values:
            return self
        item_lists = [v if is_collection(v) else [v] for v in values]
        if self.is_empty() and len(item_lists) == 1:
            return List(item_lists[0])
        items = [item for item_list in item_lists for item in item_list]
        return List(self.items[:] + items)

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[ValueT]:
        return iter(self.items)

    def __repr__(self) -> str:
        return f"List({self.items!r})"


_empty_list = List()
