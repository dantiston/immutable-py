#!/usr/bin/env python3

from typing import Generic, Iterable, Iterator

from .collection import SetCollection, ValueT


class Set(SetCollection[ValueT], Generic[ValueT]):
    def __init__(self, values: Iterable[ValueT] = ()) -> None:
        self._items = dict.fromkeys(values)

    @classmethod
    def of(cls, *values: ValueT) -> "Set":
        return Set(values) if values else _empty_set

    @classmethod
    def is_set(cls, other) -> bool:
        return isinstance(other, Set)

    def has(self, value: ValueT) -> bool:
        return value in self._items

    def add(self, value: ValueT) -> "Set":
        if value in self._items:
            return self
        return Set(list(self._items) + [value])

    def delete(self, value: ValueT) -> "Set":
        if value not in self._items:
            return self
        return Set(v for v in self._items if v != value)

    remove = delete

    def clear(self) -> "Set":
        return _empty_set

    def union(self, *others: Iterable[ValueT]) -> "Set":
        result = dict.fromkeys(self._items)
        for other in others:
            result.update(dict.fromkeys(other))
        return Set(result)

    merge = union

    def intersect(self, *others: Iterable[ValueT]) -> "Set":
        other_sets = [set(other) for other in others]
        return Set(v for v in self._items if all(v in s for s in other_sets))

    def subtract(self, *others: Iterable[ValueT]) -> "Set":
        other_sets = [set(other) for other in others]
        return Set(v for v in self._items if not any(v in s for s in other_sets))

    def is_subset(self, other: Iterable[ValueT]) -> bool:
        other_set = set(other)
        return all(v in other_set for v in self._items)

    def is_superset(self, other: Iterable[ValueT]) -> bool:
        return all(v in self._items for v in other)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[ValueT]:
        return iter(self._items)

    def __repr__(self) -> str:
        return f"Set({list(self._items)!r})"


class OrderedSet(Set[ValueT], Generic[ValueT]):
    """A Set that guarantees iteration in insertion order.

    Same rationale as `OrderedMap`: Python's `dict` (used internally for
    uniqueness + order) already preserves insertion order, so this is the
    same implementation as `Set` under a name that makes the guarantee
    explicit.
    """

    @classmethod
    def is_ordered_set(cls, other) -> bool:
        return isinstance(other, OrderedSet)


_empty_set = Set()
