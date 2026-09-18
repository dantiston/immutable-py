#!/usr/bin/env python3

import functools
import itertools

from collections import abc
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List as ListT,
    Set as SetT,
    Tuple,
    TypeVar,
)

from .equality import singleton

KeyT = TypeVar("KeyT")
ValueT = TypeVar("ValueT")
ReturnT = TypeVar("ReturnT")


def is_collection(value) -> bool:
    type_ = type(value)
    return not issubclass(type_, str) and (
        issubclass(type_, abc.Collection) or issubclass(type_, Collection)
    )


class Collection(Generic[ValueT]):
    """Shared functional surface for every persistent collection.

    Subclasses (`Indexed`, `Keyed`, `SetCollection`) provide the shape-
    specific pieces: `entries()` (how (key, value) pairs are produced),
    `_rebuild()` (how a new same-shape instance is built from entries),
    and `equals`/`__hash__` (whether order matters for equality/hashing).
    Everything else here is implemented once, generically, on top of those.
    """

    _shape: str = "collection"

    def entries(self) -> Iterator[Tuple[Any, ValueT]]:
        raise NotImplementedError

    def _rebuild(self, entries: Iterable[Tuple[Any, ValueT]]) -> "Collection":
        raise NotImplementedError

    def values(self) -> Iterator[ValueT]:
        return (v for _, v in self.entries())

    def keys(self) -> Iterator[Any]:
        return (k for k, _ in self.entries())

    def is_empty(self) -> bool:
        return len(self) == 0  # type: ignore[arg-type]

    def count(self, predicate: Callable[[ValueT], bool] = None) -> int:
        if predicate is None:
            return len(self)  # type: ignore[arg-type]
        return sum(1 for v in self.values() if predicate(v))

    def count_by(self, fn: Callable[[ValueT], Any]) -> Dict[Any, int]:
        counts: Dict[Any, int] = {}
        for v in self.values():
            key = fn(v)
            counts[key] = counts.get(key, 0) + 1
        return counts

    def to_list(self) -> ListT[ValueT]:
        return list(self.values())

    def to_set(self) -> SetT[ValueT]:
        return set(self.values())

    def join(self, separator: str = ",") -> str:
        return separator.join(str(v) for v in self.values())

    def for_each(self, fn: Callable[[ValueT], None]) -> None:
        for v in self.values():
            fn(v)

    def some(self, predicate: Callable[[ValueT], bool]) -> bool:
        return any(predicate(v) for v in self.values())

    def every(self, predicate: Callable[[ValueT], bool]) -> bool:
        return all(predicate(v) for v in self.values())

    def find(self, predicate: Callable[[ValueT], bool], nsv: ValueT = singleton) -> ValueT:
        for v in self.values():
            if predicate(v):
                return v
        if nsv is singleton:
            raise ValueError("find: no matching value")
        return nsv

    def find_last(
        self, predicate: Callable[[ValueT], bool], nsv: ValueT = singleton
    ) -> ValueT:
        result, found = nsv, False
        for v in self.values():
            if predicate(v):
                result, found = v, True
        if not found and nsv is singleton:
            raise ValueError("find_last: no matching value")
        return result

    def reduce(
        self, fn: Callable[[ReturnT, ValueT], ReturnT], initial: ReturnT = singleton
    ) -> ReturnT:
        values = self.values()
        if initial is singleton:
            return functools.reduce(fn, values)
        return functools.reduce(fn, values, initial)

    def reduce_right(
        self, fn: Callable[[ReturnT, ValueT], ReturnT], initial: ReturnT = singleton
    ) -> ReturnT:
        values = list(self.values())[::-1]
        if initial is singleton:
            return functools.reduce(fn, values)
        return functools.reduce(fn, values, initial)

    def min(self, key: Callable[[ValueT], Any] = None) -> ValueT:
        return min(self.values(), key=key)

    def max(self, key: Callable[[ValueT], Any] = None) -> ValueT:
        return max(self.values(), key=key)

    def min_by(self, fn: Callable[[ValueT], Any]) -> ValueT:
        return min(self.values(), key=fn)

    def max_by(self, fn: Callable[[ValueT], Any]) -> ValueT:
        return max(self.values(), key=fn)

    def map(self, fn: Callable[[ValueT], ReturnT]) -> "Collection[ReturnT]":
        return self._rebuild((k, fn(v)) for k, v in self.entries())

    def filter(self, predicate: Callable[[ValueT], bool]) -> "Collection[ValueT]":
        return self._rebuild((k, v) for k, v in self.entries() if predicate(v))

    def filter_not(self, predicate: Callable[[ValueT], bool]) -> "Collection[ValueT]":
        return self.filter(lambda v: not predicate(v))

    def partition(
        self, predicate: Callable[[ValueT], bool]
    ) -> Tuple["Collection[ValueT]", "Collection[ValueT]"]:
        falsy, truthy = [], []
        for k, v in self.entries():
            (truthy if predicate(v) else falsy).append((k, v))
        return self._rebuild(falsy), self._rebuild(truthy)

    def group_by(self, fn: Callable[[ValueT], Any]) -> Dict[Any, "Collection[ValueT]"]:
        groups: Dict[Any, ListT[ValueT]] = {}
        for v in self.values():
            groups.setdefault(fn(v), []).append(v)
        return {key: self._rebuild(enumerate(items)) for key, items in groups.items()}

    def reverse(self) -> "Collection[ValueT]":
        return self._rebuild(list(self.entries())[::-1])

    def sort(
        self, key: Callable[[ValueT], Any] = None, reverse: bool = False
    ) -> "Collection[ValueT]":
        sort_key = (lambda kv: kv[1]) if key is None else (lambda kv: key(kv[1]))
        return self._rebuild(sorted(self.entries(), key=sort_key, reverse=reverse))

    def sort_by(
        self, fn: Callable[[ValueT], Any], reverse: bool = False
    ) -> "Collection[ValueT]":
        return self._rebuild(
            sorted(self.entries(), key=lambda kv: fn(kv[1]), reverse=reverse)
        )

    def slice(self, start: int = None, end: int = None) -> "Collection[ValueT]":
        return self._rebuild(list(self.entries())[start:end])

    def take(self, n: int) -> "Collection[ValueT]":
        return self._rebuild(itertools.islice(self.entries(), n))

    def take_last(self, n: int) -> "Collection[ValueT]":
        entries = list(self.entries())
        return self._rebuild(entries[len(entries) - n :] if n > 0 else [])

    def take_while(self, predicate: Callable[[ValueT], bool]) -> "Collection[ValueT]":
        def gen():
            for k, v in self.entries():
                if not predicate(v):
                    return
                yield k, v

        return self._rebuild(gen())

    def take_until(self, predicate: Callable[[ValueT], bool]) -> "Collection[ValueT]":
        return self.take_while(lambda v: not predicate(v))

    def skip(self, n: int) -> "Collection[ValueT]":
        return self._rebuild(itertools.islice(self.entries(), n, None))

    def skip_last(self, n: int) -> "Collection[ValueT]":
        entries = list(self.entries())
        return self._rebuild(entries[: len(entries) - n] if n > 0 else entries)

    def skip_while(self, predicate: Callable[[ValueT], bool]) -> "Collection[ValueT]":
        def gen():
            skipping = True
            for k, v in self.entries():
                if skipping and predicate(v):
                    continue
                skipping = False
                yield k, v

        return self._rebuild(gen())

    def skip_until(self, predicate: Callable[[ValueT], bool]) -> "Collection[ValueT]":
        return self.skip_while(lambda v: not predicate(v))

    def equals(self, other) -> bool:
        raise NotImplementedError

    def __eq__(self, other) -> bool:
        if not isinstance(other, Collection):
            return NotImplemented
        return self.equals(other)

    def __repr__(self) -> str:
        name = type(self).__name__
        body = dict(self.entries()) if self._shape == "keyed" else list(self.values())
        return f"{name}({body!r})"


class Indexed(Collection, Generic[ValueT]):
    _shape = "indexed"

    def entries(self) -> Iterator[Tuple[int, ValueT]]:
        return enumerate(iter(self))

    def _rebuild(self, entries: Iterable[Tuple[Any, ValueT]]) -> "Indexed[ValueT]":
        return type(self)(v for _, v in entries)

    def has(self, index: int) -> bool:
        return -len(self) <= index < len(self)  # type: ignore[operator]

    def first(self, nsv: ValueT = singleton) -> ValueT:
        return self.get(0, nsv)

    def last(self, nsv: ValueT = singleton) -> ValueT:
        return self.get(-1, nsv)

    def includes(self, value: ValueT) -> bool:
        return any(v == value for v in self.values())

    def __contains__(self, value: ValueT) -> bool:
        return self.includes(value)

    def equals(self, other) -> bool:
        if self is other:
            return True
        if not isinstance(other, Collection) or self._shape != other._shape:
            return False
        return list(self.values()) == list(other.values())

    def __hash__(self) -> int:
        return hash((self._shape, tuple(self.values())))


class Keyed(Collection, Generic[KeyT, ValueT]):
    _shape = "keyed"

    def _rebuild(self, entries: Iterable[Tuple[KeyT, ValueT]]) -> "Keyed[KeyT, ValueT]":
        return type(self)(entries)

    def get(self, key: KeyT, nsv: ValueT = singleton) -> ValueT:
        raise NotImplementedError

    def has(self, key: KeyT) -> bool:
        raise NotImplementedError

    def __contains__(self, key: KeyT) -> bool:
        return self.has(key)

    def __iter__(self) -> Iterator[KeyT]:
        return self.keys()

    def to_dict(self) -> Dict[KeyT, ValueT]:
        return dict(self.entries())

    def equals(self, other) -> bool:
        if self is other:
            return True
        if not isinstance(other, Collection) or self._shape != other._shape:
            return False
        return dict(self.entries()) == dict(other.entries())

    def __hash__(self) -> int:
        return hash((self._shape, frozenset(self.entries())))


class SetCollection(Collection, Generic[ValueT]):
    _shape = "set"

    def entries(self) -> Iterator[Tuple[ValueT, ValueT]]:
        return ((v, v) for v in self)

    def _rebuild(self, entries: Iterable[Tuple[Any, ValueT]]) -> "SetCollection[ValueT]":
        return type(self)(v for _, v in entries)

    def has(self, value: ValueT) -> bool:
        raise NotImplementedError

    def __contains__(self, value: ValueT) -> bool:
        return self.has(value)

    def equals(self, other) -> bool:
        if self is other:
            return True
        if not isinstance(other, Collection) or self._shape != other._shape:
            return False
        return set(self.values()) == set(other.values())

    def __hash__(self) -> int:
        return hash((self._shape, frozenset(self.values())))
