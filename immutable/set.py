#!/usr/bin/env python3

from typing import Generic, Iterable, Iterator, Tuple

from .collection import SetCollection, ValueT
from .equality import singleton
from .hamt import EMPTY as _EMPTY_HAMT
from .hamt import HAMT


class Set(SetCollection[ValueT], Generic[ValueT]):
    def __init__(self, values: Iterable[ValueT] = ()) -> None:
        hamt = _EMPTY_HAMT
        for value in values:
            hamt = hamt.set(value, value)
        self._hamt = hamt

    @classmethod
    def _wrap(cls, hamt: HAMT) -> "Set":
        instance = cls.__new__(cls)
        instance._hamt = hamt
        return instance

    @classmethod
    def of(cls, *values: ValueT) -> "Set":
        return cls(values)

    @classmethod
    def is_set(cls, other) -> bool:
        return isinstance(other, Set)

    def has(self, value: ValueT) -> bool:
        return self._hamt.get(value, singleton) is not singleton

    def add(self, value: ValueT) -> "Set":
        if self.has(value):
            return self
        return type(self)._wrap(self._hamt.set(value, value))

    def delete(self, value: ValueT) -> "Set":
        new_hamt = self._hamt.delete(value)
        if new_hamt is self._hamt:
            return self
        return type(self)._wrap(new_hamt)

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
        return len(self._hamt)

    def __iter__(self) -> Iterator[ValueT]:
        return (k for k, _ in self._hamt)

    def __repr__(self) -> str:
        return f"Set({list(self)!r})"


class OrderedSet(Set[ValueT], Generic[ValueT]):
    """A Set that guarantees iteration in insertion order.

    Same rationale as `OrderedMap`: `Set` iterates in HAMT (hash-bucket)
    order, `OrderedSet` additionally tracks insertion order explicitly.
    """

    def __init__(self, values: Iterable[ValueT] = ()) -> None:
        hamt = _EMPTY_HAMT
        order = []
        for value in values:
            if hamt.get(value, singleton) is singleton:
                order.append(value)
            hamt = hamt.set(value, value)
        self._hamt = hamt
        self._order = tuple(order)

    @classmethod
    def _wrap(cls, hamt: HAMT, order: Tuple[ValueT, ...]) -> "OrderedSet":
        instance = cls.__new__(cls)
        instance._hamt = hamt
        instance._order = order
        return instance

    @classmethod
    def is_ordered_set(cls, other) -> bool:
        return isinstance(other, OrderedSet)

    def add(self, value: ValueT) -> "OrderedSet":
        if self.has(value):
            return self
        return OrderedSet._wrap(self._hamt.set(value, value), self._order + (value,))

    def delete(self, value: ValueT) -> "OrderedSet":
        new_hamt = self._hamt.delete(value)
        if new_hamt is self._hamt:
            return self
        new_order = tuple(v for v in self._order if v != value)
        return OrderedSet._wrap(new_hamt, new_order)

    remove = delete

    def clear(self) -> "OrderedSet":
        return OrderedSet()

    def __iter__(self) -> Iterator[ValueT]:
        return iter(self._order)
