#!/usr/bin/env python3

from typing import ClassVar, Generic, Iterable, Iterator, Type

from .collection import SetCollection, ValueT
from .map import Map, OrderedMap


class Set(SetCollection[ValueT], Generic[ValueT]):
    # The Map subtype used internally to store `value -> value`.
    # `OrderedSet` overrides only this, reusing every method below as-is -
    # mirroring how Immutable.js's OrderedSet is a Set whose `_map` happens
    # to be an OrderedMap rather than a Map.
    _map_class: ClassVar[Type[Map]] = Map

    def __init__(self, values: Iterable[ValueT] = ()) -> None:
        self._map = self._map_class((v, v) for v in values)

    @classmethod
    def _wrap(cls, map_: Map) -> "Set":
        instance = cls.__new__(cls)
        instance._map = map_
        return instance

    @classmethod
    def of(cls, *values: ValueT) -> "Set":
        return cls(values)

    @classmethod
    def is_set(cls, other) -> bool:
        return isinstance(other, Set)

    def has(self, value: ValueT) -> bool:
        return self._map.has(value)

    def add(self, value: ValueT) -> "Set":
        if self.has(value):
            return self
        return type(self)._wrap(self._map.set(value, value))

    def delete(self, value: ValueT) -> "Set":
        new_map = self._map.delete(value)
        if new_map is self._map:
            return self
        return type(self)._wrap(new_map)

    remove = delete

    def clear(self) -> "Set":
        return type(self)()

    def union(self, *others: Iterable[ValueT]) -> "Set":
        result = self
        for other in others:
            for value in other:
                result = result.add(value)
        return result

    merge = union

    def intersect(self, *others: Iterable[ValueT]) -> "Set":
        other_sets = [set(other) for other in others]
        return type(self)(v for v in self if all(v in s for s in other_sets))

    def subtract(self, *others: Iterable[ValueT]) -> "Set":
        other_sets = [set(other) for other in others]
        return type(self)(v for v in self if not any(v in s for s in other_sets))

    def is_subset(self, other: Iterable[ValueT]) -> bool:
        other_set = set(other)
        return all(v in other_set for v in self)

    def is_superset(self, other: Iterable[ValueT]) -> bool:
        return all(self.has(v) for v in other)

    def __len__(self) -> int:
        return len(self._map)

    def __iter__(self) -> Iterator[ValueT]:
        return iter(self._map.keys())

    def __repr__(self) -> str:
        return f"{type(self).__name__}({list(self)!r})"


class OrderedSet(Set[ValueT], Generic[ValueT]):
    """A Set that guarantees iteration in insertion order.

    The entire implementation is inherited from `Set` unchanged - only
    `_map_class` differs, so every method that goes through `self._map`
    (`has`, `add`, `delete`, `__iter__`, `__len__`, ...) picks up
    `OrderedMap`'s insertion-order guarantee for free. This is exactly
    how Immutable.js's `OrderedSet` relates to `Set`.
    """

    _map_class: ClassVar[Type[Map]] = OrderedMap

    @classmethod
    def is_ordered_set(cls, other) -> bool:
        return isinstance(other, OrderedSet)
