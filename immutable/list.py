#!/usr/bin/env python3

from typing import Callable, Generic, Iterable, Iterator, Union

from .collection import Indexed, ReturnT, ValueT, is_collection
from .equality import singleton
from .vector import Vector


class List(Indexed[ValueT], Generic[ValueT]):
    def __init__(self, items: Iterable[ValueT] = ()) -> None:
        self._vector = Vector.from_iterable(items)

    @classmethod
    def _wrap(cls, vector: Vector) -> "List":
        instance = cls.__new__(cls)
        instance._vector = vector
        return instance

    @classmethod
    def of(cls, *items: ValueT) -> "List":
        return List(items) if items else _empty_list

    @classmethod
    def is_list(cls, other) -> bool:
        return isinstance(other, List)

    def get(self, index: int, nsv: ValueT = singleton) -> ValueT:
        index = self._normalize_index(index)
        try:
            return self._vector.get(index)
        except IndexError:
            if nsv is singleton:
                raise
            return nsv

    def _normalize_index(self, index: int) -> int:
        return index + len(self._vector) if index < 0 else index

    def set(self, index: int, value: ValueT) -> "List":
        index = self._normalize_index(index)
        if index < 0:
            return self
        vector = self._vector
        if index >= len(vector):
            for _ in range(index - len(vector)):
                vector = vector.push(None)
            vector = vector.push(value)
        else:
            vector = vector.set(index, value)
        return List._wrap(vector)

    def delete(self, index: int) -> "List":
        index = self._normalize_index(index)
        if not 0 <= index < len(self._vector):
            return self
        items = list(self._vector)
        items.pop(index)
        return List(items)

    remove = delete

    def insert(self, index: int, value: ValueT) -> "List":
        items = list(self._vector)
        items.insert(index, value)
        return List(items)

    def push(self, *values: ValueT) -> "List":
        vector = self._vector
        for value in values:
            vector = vector.push(value)
        return List._wrap(vector)

    def pop(self) -> "List":
        if not self._vector:
            return self
        return List._wrap(self._vector.pop())

    def unshift(self, *values: ValueT) -> "List":
        return List(list(values) + list(self._vector))

    def shift(self) -> "List":
        return List(list(self._vector)[1:])

    def update(
        self,
        index: int,
        updater: Callable[[ValueT], ValueT],
        nsv: ValueT = singleton,
    ) -> "List":
        return self.set(index, updater(self.get(index, nsv)))

    def set_size(self, size: int) -> "List":
        n = len(self._vector)
        if size < n:
            return List(list(self._vector)[:size])
        if size > n:
            vector = self._vector
            for _ in range(size - n):
                vector = vector.push(None)
            return List._wrap(vector)
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
        vector = self._vector
        for item_list in item_lists:
            for item in item_list:
                vector = vector.push(item)
        return List._wrap(vector)

    def __len__(self) -> int:
        return len(self._vector)

    def __iter__(self) -> Iterator[ValueT]:
        return iter(self._vector)

    def __repr__(self) -> str:
        return f"List({list(self._vector)!r})"


_empty_list = List()
