#!/usr/bin/env python3

from typing import Callable, Generic, Iterable, Iterator, Tuple, Union

from .collection import KeyT, Keyed, ValueT
from .equality import singleton
from .list import List


class Map(Keyed[KeyT, ValueT], Generic[KeyT, ValueT]):
    def __init__(
        self,
        pairs: Union[Iterable[Tuple[KeyT, ValueT]], "Map", dict] = (),
    ) -> None:
        if isinstance(pairs, Map):
            self._dict = dict(pairs._dict)
        elif isinstance(pairs, dict):
            self._dict = dict(pairs)
        else:
            self._dict = dict(pairs)

    @classmethod
    def is_map(cls, other) -> bool:
        return isinstance(other, Map)

    def entries(self) -> Iterator[Tuple[KeyT, ValueT]]:
        return iter(self._dict.items())

    def get(self, key: KeyT, nsv: ValueT = singleton) -> ValueT:
        if key in self._dict:
            return self._dict[key]
        if nsv is singleton:
            raise KeyError(key)
        return nsv

    def has(self, key: KeyT) -> bool:
        return key in self._dict

    def set(self, key: KeyT, value: ValueT) -> "Map":
        result = dict(self._dict)
        result[key] = value
        return Map(result)

    def delete(self, key: KeyT) -> "Map":
        if key not in self._dict:
            return self
        result = dict(self._dict)
        del result[key]
        return Map(result)

    remove = delete

    def update(
        self, key: KeyT, updater: Callable[[ValueT], ValueT], nsv: ValueT = None
    ) -> "Map":
        return self.set(key, updater(self._dict.get(key, nsv)))

    def clear(self) -> "Map":
        return _empty_map

    def flip(self) -> "Map":
        return Map((v, k) for k, v in self._dict.items())

    def merge(self, *others: Iterable) -> "Map":
        result = dict(self._dict)
        for other in others:
            result.update(_as_pairs(other))
        return Map(result)

    def merge_with(
        self, fn: Callable[[ValueT, ValueT], ValueT], *others: Iterable
    ) -> "Map":
        result = dict(self._dict)
        for other in others:
            for key, value in _as_pairs(other):
                result[key] = fn(result[key], value) if key in result else value
        return Map(result)

    def merge_deep(self, *others: Iterable) -> "Map":
        result = self
        for other in others:
            for key, value in _as_pairs(other):
                existing = result._dict.get(key, singleton)
                if isinstance(existing, Map) and isinstance(value, Map):
                    result = result.set(key, existing.merge_deep(value))
                else:
                    result = result.set(key, value)
        return result

    def get_in(self, path: Iterable, nsv=singleton):
        current = self
        for key in path:
            current = _get_path_segment(current, key)
            if current is singleton:
                break
        if current is singleton:
            if nsv is singleton:
                raise KeyError(list(path))
            return nsv
        return current

    def set_in(self, path: Iterable, value) -> "Map":
        return self.update_in(path, lambda _: value)

    def update_in(self, path: Iterable, updater: Callable) -> "Map":
        path = list(path)
        if not path:
            return updater(self)
        key, rest = path[0], path[1:]
        existing = self._dict.get(key, singleton)
        if rest:
            child = existing if isinstance(existing, Map) else Map()
            new_child = child.update_in(rest, updater)
        else:
            new_child = updater(None if existing is singleton else existing)
        return self.set(key, new_child)

    def delete_in(self, path: Iterable) -> "Map":
        path = list(path)
        if not path:
            return self
        key, rest = path[0], path[1:]
        if key not in self._dict:
            return self
        if not rest:
            return self.delete(key)
        child = self._dict[key]
        if not isinstance(child, Map):
            return self
        return self.set(key, child.delete_in(rest))

    def __len__(self) -> int:
        return len(self._dict)

    def __repr__(self) -> str:
        return f"Map({self._dict!r})"


class OrderedMap(Map[KeyT, ValueT], Generic[KeyT, ValueT]):
    """A Map that guarantees iteration in insertion order.

    Python's `dict` already preserves insertion order (3.7+), so this is
    the same implementation as `Map` — the distinct type exists to match
    Immutable.js's API and to make the ordering guarantee explicit in
    calling code, even though `Map` here behaves identically.
    """

    @classmethod
    def is_ordered_map(cls, other) -> bool:
        return isinstance(other, OrderedMap)


def _as_pairs(other) -> Iterator[Tuple]:
    if isinstance(other, Keyed):
        return iter(other.entries())
    if isinstance(other, dict):
        return iter(other.items())
    return iter(other)


def _get_path_segment(current, key):
    if isinstance(current, Map):
        return current._dict.get(key, singleton)
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


_empty_map = Map()
