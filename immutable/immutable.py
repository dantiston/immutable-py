#!/usr/bin/env python3

from collections import abc
from typing import Iterable, Iterator, Callable, Generic, Tuple, TypeVar, Union

KeyT = TypeVar("KeyT")
ValueT = TypeVar("ValueT")
ReturnT = TypeVar("ReturnT")

singleton = object()


def is_collection(value) -> bool:
    type_ = type(value)
    return not issubclass(type_, str) and (
        issubclass(type_, abc.Collection) or issubclass(type_, Collection)
    )


class Collection(Generic[ValueT]):
    pass


class Indexed(Collection, Generic[ValueT]):
    def has(self, index: int) -> bool:
        return index < len(self)

    def first(self, nsv: ValueT = singleton) -> ValueT:
        return self.get(0, nsv)

    def last(self, nsv: ValueT = singleton) -> ValueT:
        return self.get(-1, nsv)

    def __contains__(self, value: ValueT) -> bool:
        return self.includes(value)


class List(Indexed, Generic[ValueT]):
    def __init__(self, items: Iterable[ValueT] = ()) -> None:
        self.items = list(items)

    @classmethod
    def of(cls, *items: Tuple[ValueT]) -> "List":
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

    def includes(self, value: ValueT) -> bool:
        return value in self.items

    def set(self, index: int, value: ValueT) -> "List":
        result = self.items[:]
        result[index] = value
        return List(result)

    def delete(self, index: int) -> "List":
        result = self.items[:]
        result.pop(index)
        return List(result)

    def insert(self, index: int, value: ValueT) -> "List":
        result = self.items[:]
        result.insert(index, value)
        return List(result)

    def push(self, *values: Tuple[ValueT]) -> "List":
        return List(self.items[:] + list(values))

    def pop(self, *values: Tuple[ValueT]) -> "List":
        return List(self.items[:-1])

    def unshift(self, *values: Tuple[ValueT]) -> "List":
        return List(list(values) + self.items[:])

    def shift(self) -> "List":
        return List(self.items[1:])

    def update(
        self, index: int, updater: Callable[[ValueT], ValueT], nsv: ValueT = singleton
    ) -> "List":
        return self.set(index, updater(self.get(index, nsv)))

    def thru(self, updater: Callable[["List"], ReturnT]) -> ReturnT:
        return updater(self)

    def clear(self) -> "List":
        return _empty_list

    def concat(self, *values: Tuple[Union[Iterable[ValueT], ValueT]]) -> "List":
        if not values:
            return self
        item_lists = [
            value if is_collection(value) else [value] for value in values if value
        ]
        if not item_lists:
            return self
        if self.is_empty() and len(item_lists) == 1:
            return List(item_lists[0])
        items = [item for item_list in item_lists for item in item_list]
        return List(self.items[:] + items)

    def map(self, updater: Callable[["List"], ReturnT]) -> ReturnT:
        return List(updater(self.items[:]))

    def is_empty(self) -> bool:
        return len(self) == 0

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[ValueT]:
        return iter(self.items)


_empty_list = List()
