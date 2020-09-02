#!/usr/bin/env python3

"""
immutable.py

A library providing many Persistent Immutable data structures based on
Immutable.js, focusing on both mimicking Immutable.js' API and feeling
pythonic. Immutable.py includes List.
"""

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

from immutable.vector import _empty_vector, Vector

KeyT = TypeVar("KeyT")
ValueT = TypeVar("ValueT")
ReturnT = TypeVar("ReturnT")

from immutable.shared import singleton


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

    def is_empty(self) -> bool:
        return len(self) == 0


class List(Indexed, Generic[ValueT]):
    def __init__(self, items: Iterable[ValueT] = ()) -> None:
        self.vector = _empty_vector.concat(items)

    @classmethod
    def _of_vector(cls, vector: Vector) -> "List":
        if not vector:
            return _empty_list
        result = List()
        result.vector = vector
        return result

    @classmethod
    def of(cls, *items: Tuple[ValueT]) -> "List":
        return List(items) if items else _empty_list

    @classmethod
    def is_list(cls, other) -> bool:
        return isinstance(other, List)

    def get(self, index: int, nsv: ValueT = singleton) -> ValueT:
        return self.vector.get(index if index >= 0 else len(self) + index, nsv=nsv)

    def includes(self, value: ValueT) -> bool:
        return value in self.vector

    def set(self, index: int, value: ValueT) -> "List":
        return List._of_vector(self.vector.set(index, value))

    def delete(self, index: int) -> "List":
        return self.pop(index)

    def remove(self, value: ValueT) -> "List":
        return List._of_vector(self.vector.remove(value))

    def insert(self, index: int, value: ValueT) -> "List":
        """Naive for now"""
        current = self.vector._get_list()
        return _empty_list.concat(current[:index]).push(value).concat(current[index:])

    def push(self, *values: Tuple[ValueT]) -> "List":
        return List._of_vector(self.vector.concat(values))

    def pop(self, i: int = None) -> "List":
        return List._of_vector(self.vector.pop(i))

    def unshift(self, *values: Tuple[ValueT]) -> "List":
        """Naive for now"""
        return _empty_list.concat(values).concat(self)

    def shift(self) -> "List":
        return List._of_vector(self.vector.shift())

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
            value if is_collection(value) else [value]
            for value in values
        ]
        if not item_lists:
            return self
        if self.is_empty() and len(item_lists) == 1:
            return List(item_lists[0])
        items = [item for item_list in item_lists for item in item_list]
        return List._of_vector(self.vector.concat(items))

    def map(self, updater: Callable[[ValueT], ReturnT]) -> "List":
        return List(map(updater, self.vector))

    def flat_map(
        self, updater: Callable[[Union[Iterable[ValueT], ValueT]], ReturnT]
    ) -> "List":
        item_lists = [item if is_collection(item) else [item] for item in self.vector]
        items = [item for item_list in item_lists for item in item_list]
        return List(map(updater, items))

    def filter(self, predicate: Callable[[ValueT], bool] = None) -> "List":
        return List(filter(predicate, self.vector))

    def zip(self, *other: Tuple[Iterable[ValueT]]) -> "List":
        return List(zip(self.vector, *other))

    def zip_all(self, *other: Tuple[Iterable[ValueT]]) -> "List":
        return List(zip_longest(self.vector, *other))

    def zip_longest(self, *other: Tuple[Iterable[ValueT]]) -> "List":
        return self.zip_all(*other)

    def zip_with(
        self, zipper: Callable[[ValueT, ValueT], ValueT], other: Iterable[ValueT]
    ) -> "List":
        return List(zipper(l, r) for l, r in zip(self.vector, other))

    def __len__(self) -> int:
        return len(self.vector)

    def __iter__(self) -> Iterator[ValueT]:
        return iter(self.vector)

    def __str__(self) -> str:
        return str(self.vector)

    def __repr__(self) -> str:
        return f"List({self.vector._get_list()})"


_empty_list = List()
