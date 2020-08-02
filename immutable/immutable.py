#!/usr/bin/env python3

from collections import abc
from itertools import zip_longest
from typing import (
    Collection as CollectionT,
    Iterable,
    Iterator,
    Callable,
    Generic,
    Tuple,
    TypeVar,
    Union,
)

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
        return List.of(*self.items[:index], value, *self.items[index + 1 :])

    def delete(self, index: int) -> "List":
        result = self.items[:]
        result.pop(index)
        return List(result)

    def insert(self, index: int, value: ValueT) -> "List":
        result = self.items[:]
        result.insert(index, value)
        return List(result)

    def push(self, *values: Tuple[ValueT]) -> "List":
        return List(self.items + list(values))

    def pop(self, *values: Tuple[ValueT]) -> "List":
        return List(self.items[:-1])

    def unshift(self, *values: Tuple[ValueT]) -> "List":
        return List(list(values) + self.items)

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
        return List(self.items + items)

    def map(self, updater: Callable[[ValueT], ReturnT]) -> "List":
        return List(map(updater, self.items))

    def flat_map(
        self, updater: Callable[[Union[Iterable[ValueT], ValueT]], ReturnT]
    ) -> "List":
        item_lists = [item if is_collection(item) else [item] for item in self.items]
        items = [item for item_list in item_lists for item in item_list]
        return List(map(updater, items))

    def filter(self, predicate: Callable[[ValueT], bool] = None) -> "List":
        return List(filter(predicate, self.items))

    def zip(self, *other: Tuple[Iterable[ValueT]]) -> "List":
        return List(zip(self.items, *other))

    def zip_all(self, *other: Tuple[Iterable[ValueT]]) -> "List":
        return List(zip_longest(self.items, *other))

    def zip_longest(self, *other: Tuple[Iterable[ValueT]]) -> "List":
        return self.zip_all(*other)

    def zip_with(
        self, zipper: Callable[[ValueT, ValueT], ValueT], other: Iterable[ValueT]
    ) -> "List":
        return List(zipper(l, r) for l, r in zip(self.items, other))

    def is_empty(self) -> bool:
        return len(self) == 0

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[ValueT]:
        return iter(self.items)


_empty_list = List()
