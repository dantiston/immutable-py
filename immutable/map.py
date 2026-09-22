#!/usr/bin/env python3

from typing import Callable, Generic, Iterable, Iterator, Tuple, Union

from .collection import KeyT, Keyed, ValueT
from .equality import singleton
from .hamt import EMPTY as _EMPTY_HAMT
from .hamt import HAMT
from .list import List
from .vector import EMPTY as _EMPTY_VECTOR
from .vector import WIDTH as _TRIE_WIDTH
from .vector import Vector


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

    def _probe(self, key: KeyT):
        """The value at `key`, or the `singleton` sentinel if absent.

        Unlike `get`, this never raises - it's the polymorphic primitive
        every "does this key exist, and if so what's its value" call site
        below uses, so each subtype (just `OrderedMap`, for now) only has
        to override this one method to get correct `get`/`has`/`merge*`/
        `*_in` behavior for free via inheritance.
        """
        return self._hamt.get(key, singleton)

    def get(self, key: KeyT, nsv: ValueT = singleton) -> ValueT:
        value = self._probe(key)
        if value is singleton:
            if nsv is singleton:
                raise KeyError(key)
            return nsv
        return value

    def has(self, key: KeyT) -> bool:
        return self._probe(key) is not singleton

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
        current = self._probe(key)
        return self.set(key, updater(nsv if current is singleton else current))

    def clear(self) -> "Map":
        return type(self)()

    def flip(self) -> "Map":
        return type(self)((v, k) for k, v in self.entries())

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
                existing = result._probe(key)
                result = result.set(
                    key, fn(existing, value) if existing is not singleton else value
                )
        return result

    def merge_deep(self, *others: Iterable) -> "Map":
        result = self
        for other in others:
            for key, value in _as_pairs(other):
                existing = result._probe(key)
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
        existing = self._probe(key)
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
        existing = self._probe(key)
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
        return f"{type(self).__name__}({dict(self.entries())!r})"


class OrderedMap(Map[KeyT, ValueT], Generic[KeyT, ValueT]):
    """A Map that guarantees iteration in insertion order.

    Mirrors Immutable.js's actual `OrderedMap`: it's backed by *both* a
    HAMT and a vector trie, not just an order-tracking list bolted onto a
    HAMT-backed Map.

    - `_index` is a HAMT mapping each key to its position (an int) in
      `_entries`.
    - `_entries` is a `Vector` holding `(key, value)` pairs in insertion
      order - or `None` at a deleted position, since removing from the
      middle of a vector trie is O(n) and we'd rather not pay that on
      every delete.

    `set` on an existing key overwrites its `_entries` slot in place
    (no reorder, matching Immutable.js and Python `dict` semantics); on a
    new key it appends. `delete` pops `_entries` if the key was the most
    recently appended live entry (cheap), otherwise leaves a `None`
    tombstone. Tombstones accumulate until `_entries` has grown to at
    least the trie's branching width (`_TRIE_WIDTH`, 32) *and* is at
    least double the live entry count - at that point `_entries` is
    rebuilt with just the live entries and `_index` is rebuilt to match,
    same threshold Immutable.js uses.
    """

    def __init__(
        self,
        pairs: Union[Iterable[Tuple[KeyT, ValueT]], "Map", dict] = (),
    ) -> None:
        if isinstance(pairs, OrderedMap):
            self._index = pairs._index
            self._entries = pairs._entries
            return
        if isinstance(pairs, Map):
            pairs = pairs.entries()
        elif isinstance(pairs, dict):
            pairs = pairs.items()
        index, entries = _EMPTY_HAMT, _EMPTY_VECTOR
        for key, value in pairs:
            index, entries = _ordered_map_set(index, entries, key, value)
        self._index = index
        self._entries = entries

    @classmethod
    def _wrap(cls, index: HAMT, entries: Vector) -> "OrderedMap":
        instance = cls.__new__(cls)
        instance._index = index
        instance._entries = entries
        return instance

    @classmethod
    def is_ordered_map(cls, other) -> bool:
        return isinstance(other, OrderedMap)

    def entries(self) -> Iterator[Tuple[KeyT, ValueT]]:
        return (entry for entry in self._entries if entry is not None)

    def _probe(self, key: KeyT):
        idx = self._index.get(key, singleton)
        if idx is singleton:
            return singleton
        return self._entries.get(idx)[1]

    def set(self, key: KeyT, value: ValueT) -> "OrderedMap":
        new_index, new_entries = _ordered_map_set(self._index, self._entries, key, value)
        return OrderedMap._wrap(new_index, new_entries)

    def delete(self, key: KeyT) -> "OrderedMap":
        new_index, new_entries = _ordered_map_delete(self._index, self._entries, key)
        if new_index is self._index:
            return self
        return OrderedMap._wrap(new_index, new_entries)

    remove = delete

    def clear(self) -> "OrderedMap":
        return OrderedMap()

    def __len__(self) -> int:
        return len(self._index)


def _ordered_map_set(
    index: HAMT, entries: Vector, key, value
) -> Tuple[HAMT, Vector]:
    idx = index.get(key, singleton)
    if idx is singleton:
        return index.set(key, len(entries)), entries.push((key, value))
    return index, entries.set(idx, (key, value))


def _ordered_map_delete(index: HAMT, entries: Vector, key) -> Tuple[HAMT, Vector]:
    idx = index.get(key, singleton)
    if idx is singleton:
        return index, entries
    new_index = index.delete(key)
    if idx == len(entries) - 1:
        new_entries = entries.pop()
    else:
        new_entries = entries.set(idx, None)
    if len(new_entries) >= _TRIE_WIDTH and len(new_entries) >= 2 * len(new_index):
        new_index, new_entries = _compact_ordered_map(new_index, new_entries)
    return new_index, new_entries


def _compact_ordered_map(index: HAMT, entries: Vector) -> Tuple[HAMT, Vector]:
    live_entries = [entry for entry in entries if entry is not None]
    new_entries = Vector.from_iterable(live_entries)
    new_index = _EMPTY_HAMT
    for position, (key, _value) in enumerate(live_entries):
        new_index = new_index.set(key, position)
    return new_index, new_entries


def _as_pairs(other) -> Iterator[Tuple]:
    if isinstance(other, Keyed):
        return iter(other.entries())
    if isinstance(other, dict):
        return iter(other.items())
    return iter(other)


def _get_path_segment(current, key):
    if isinstance(current, Map):
        return current._probe(key)
    if isinstance(current, List):
        try:
            return current.get(key)
        except IndexError:
            return singleton
    if isinstance(current, dict):
        return current.get(key, singleton)
    if isinstance(current, (list, tuple)):
        try:
            return current[key]
        except (IndexError, TypeError):
            return singleton
    return singleton
