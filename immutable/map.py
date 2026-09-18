#!/usr/bin/env python3

from typing import Callable, Generic, Iterable, Iterator, Tuple, Union

from .collection import KeyT, Keyed, ValueT
from .equality import singleton
from .hamt import EMPTY as _EMPTY_HAMT
from .hamt import HAMT
from .list import List


class Map(Keyed[KeyT, ValueT], Generic[KeyT, ValueT]):
    def __init__(
        self,
        pairs: Union[Iterable[Tuple[KeyT, ValueT]], "Map", dict] = (),
    ) -> None:
        if isinstance(pairs, Map):
            self._hamt = pairs._hamt
            return
        if isinstance(pairs, dict):
            pairs = pairs.items()
        hamt = _EMPTY_HAMT
        for key, value in pairs:
            hamt = hamt.set(key, value)
        self._hamt = hamt

    @classmethod
    def _wrap(cls, hamt: HAMT) -> "Map":
        instance = cls.__new__(cls)
        instance._hamt = hamt
        return instance

    @classmethod
    def is_map(cls, other) -> bool:
        return isinstance(other, Map)

    def entries(self) -> Iterator[Tuple[KeyT, ValueT]]:
        return iter(self._hamt)

    def get(self, key: KeyT, nsv: ValueT = singleton) -> ValueT:
        value = self._hamt.get(key, singleton)
        if value is singleton:
            if nsv is singleton:
                raise KeyError(key)
            return nsv
        return value

    def has(self, key: KeyT) -> bool:
        return self._hamt.get(key, singleton) is not singleton

    def set(self, key: KeyT, value: ValueT) -> "Map":
        return type(self)._wrap(self._hamt.set(key, value))

    def delete(self, key: KeyT) -> "Map":
        new_hamt = self._hamt.delete(key)
        if new_hamt is self._hamt:
            return self
        return type(self)._wrap(new_hamt)

    remove = delete

    def update(
        self, key: KeyT, updater: Callable[[ValueT], ValueT], nsv: ValueT = None
    ) -> "Map":
        current = self._hamt.get(key, singleton)
        return self.set(key, updater(nsv if current is singleton else current))

    def clear(self) -> "Map":
        return type(self)()

    def flip(self) -> "Map":
        return Map((v, k) for k, v in self.entries())

    def merge(self, *others: Iterable) -> "Map":
        result = self
        for other in others:
            for key, value in _as_pairs(other):
                result = result.set(key, value)
        return result

    def merge_with(
        self, fn: Callable[[ValueT, ValueT], ValueT], *others: Iterable
    ) -> "Map":
        result = self
        for other in others:
            for key, value in _as_pairs(other):
                existing = result._hamt.get(key, singleton)
                result = result.set(
                    key, fn(existing, value) if existing is not singleton else value
                )
        return result

    def merge_deep(self, *others: Iterable) -> "Map":
        result = self
        for other in others:
            for key, value in _as_pairs(other):
                existing = result._hamt.get(key, singleton)
                if isinstance(existing, Map) and isinstance(value, Map):
                    result = result.set(key, existing.merge_deep(value))
                else:
                    result = result.set(key, value)
        return result

    def get_in(self, path: Iterable, nsv=singleton):
        path = list(path)
        current = self
        for key in path:
            current = _get_path_segment(current, key)
            if current is singleton:
                break
        if current is singleton:
            if nsv is singleton:
                raise KeyError(path)
            return nsv
        return current

    def set_in(self, path: Iterable, value) -> "Map":
        return self.update_in(path, lambda _: value)

    def update_in(self, path: Iterable, updater: Callable) -> "Map":
        path = list(path)
        if not path:
            return updater(self)
        key, rest = path[0], path[1:]
        existing = self._hamt.get(key, singleton)
        if rest:
            child = existing if isinstance(existing, Map) else type(self)()
            new_child = child.update_in(rest, updater)
        else:
            new_child = updater(None if existing is singleton else existing)
        return self.set(key, new_child)

    def delete_in(self, path: Iterable) -> "Map":
        path = list(path)
        if not path:
            return self
        key, rest = path[0], path[1:]
        existing = self._hamt.get(key, singleton)
        if existing is singleton:
            return self
        if not rest:
            return self.delete(key)
        if not isinstance(existing, Map):
            return self
        return self.set(key, existing.delete_in(rest))

    def __len__(self) -> int:
        return len(self._hamt)

    def __repr__(self) -> str:
        return f"Map({dict(self.entries())!r})"


class OrderedMap(Map[KeyT, ValueT], Generic[KeyT, ValueT]):
    """A Map that guarantees iteration in insertion order.

    `Map` iterates in HAMT (hash-bucket) order, same as Immutable.js's
    unordered Map. `OrderedMap` additionally tracks insertion order as a
    tuple of keys alongside the trie; re-`set`-ing an existing key updates
    its value in place without moving its position, matching Immutable.js
    (and Python `dict`) semantics.
    """

    def __init__(
        self,
        pairs: Union[Iterable[Tuple[KeyT, ValueT]], "Map", dict] = (),
    ) -> None:
        if isinstance(pairs, OrderedMap):
            self._hamt = pairs._hamt
            self._order = pairs._order
            return
        if isinstance(pairs, Map):
            pairs = pairs.entries()
        elif isinstance(pairs, dict):
            pairs = pairs.items()
        hamt = _EMPTY_HAMT
        order = []
        for key, value in pairs:
            if hamt.get(key, singleton) is singleton:
                order.append(key)
            hamt = hamt.set(key, value)
        self._hamt = hamt
        self._order = tuple(order)

    @classmethod
    def _wrap(cls, hamt: HAMT, order: Tuple[KeyT, ...]) -> "OrderedMap":
        instance = cls.__new__(cls)
        instance._hamt = hamt
        instance._order = order
        return instance

    @classmethod
    def is_ordered_map(cls, other) -> bool:
        return isinstance(other, OrderedMap)

    def entries(self) -> Iterator[Tuple[KeyT, ValueT]]:
        return ((key, self._hamt.get(key)) for key in self._order)

    def set(self, key: KeyT, value: ValueT) -> "OrderedMap":
        existed = self._hamt.get(key, singleton) is not singleton
        new_hamt = self._hamt.set(key, value)
        new_order = self._order if existed else self._order + (key,)
        return OrderedMap._wrap(new_hamt, new_order)

    def delete(self, key: KeyT) -> "OrderedMap":
        new_hamt = self._hamt.delete(key)
        if new_hamt is self._hamt:
            return self
        new_order = tuple(k for k in self._order if k != key)
        return OrderedMap._wrap(new_hamt, new_order)

    remove = delete

    def clear(self) -> "OrderedMap":
        return OrderedMap()


def _as_pairs(other) -> Iterator[Tuple]:
    if isinstance(other, Keyed):
        return iter(other.entries())
    if isinstance(other, dict):
        return iter(other.items())
    return iter(other)


def _get_path_segment(current, key):
    if isinstance(current, Map):
        return current._hamt.get(key, singleton)
    if isinstance(current, List):
        return current.get(key, singleton)
    if isinstance(current, dict):
        return current.get(key, singleton)
    if isinstance(current, (list, tuple)):
        try:
            return current[key]
        except (IndexError, TypeError):
            return singleton
    return singleton
