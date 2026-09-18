#!/usr/bin/env python3

"""A persistent hash array mapped trie (HAMT).

This is the structural-sharing backing for `Map` and `Set`: writes are
O(log32 n) instead of the O(n) full-copy the earlier dict-backed
implementation used, and old versions stay valid/unchanged after a write
because only the path to the changed entry is ever reallocated.

Layout, per level of the trie:
  - 5 bits of the key's hash select one of 32 children at that level
    (`HASH_BITS` / `HASH_MASK`).
  - A `_BitmapNode` stores only its *occupied* slots, compacted into a
    tuple in popcount order, with a bitmap marking which of the 32 slots
    are present. Each occupied slot holds either a leaf `(key, value)`
    pair or a child node, so a single-entry subtree costs one tuple slot,
    not a whole extra node.
  - If two keys still collide after all bits of the hash are consumed
    (a genuine hash collision, not just a shared prefix), a
    `_CollisionNode` holds them as a flat list instead of recursing
    forever.

The empty trie is represented by `root=None` on `HAMT` rather than a
sentinel node, so an empty `HAMT` is a cheap, allocation-free constant.
"""

from typing import Any, Iterator, Tuple, Union

from .equality import singleton

HASH_BITS = 5
HASH_MASK = (1 << HASH_BITS) - 1
HASH_WIDTH = 64
_MASK64 = (1 << HASH_WIDTH) - 1


def _hash_of(key: Any) -> int:
    return hash(key) & _MASK64


def _fragment(h: int, shift: int) -> int:
    return (h >> shift) & HASH_MASK


def _popcount(x: int) -> int:
    return bin(x).count("1")


class _Node:
    __slots__ = ()

    def get(self, h: int, shift: int, key: Any, nsv: Any) -> Any:
        raise NotImplementedError

    def set(self, h: int, shift: int, key: Any, value: Any) -> "_Node":
        raise NotImplementedError

    def delete(self, h: int, shift: int, key: Any) -> Union["_Node", None]:
        raise NotImplementedError

    def iter_entries(self) -> Iterator[Tuple[Any, Any]]:
        raise NotImplementedError


class _BitmapNode(_Node):
    __slots__ = ("bitmap", "entries")

    def __init__(self, bitmap: int, entries: tuple) -> None:
        self.bitmap = bitmap
        self.entries = entries

    def get(self, h: int, shift: int, key: Any, nsv: Any) -> Any:
        bit = 1 << _fragment(h, shift)
        if not self.bitmap & bit:
            return nsv
        idx = _popcount(self.bitmap & (bit - 1))
        entry = self.entries[idx]
        if isinstance(entry, _Node):
            return entry.get(h, shift + HASH_BITS, key, nsv)
        k, v = entry
        return v if k == key else nsv

    def set(self, h: int, shift: int, key: Any, value: Any) -> "_Node":
        frag = _fragment(h, shift)
        bit = 1 << frag
        idx = _popcount(self.bitmap & (bit - 1))
        if self.bitmap & bit:
            entry = self.entries[idx]
            if isinstance(entry, _Node):
                new_child = entry.set(h, shift + HASH_BITS, key, value)
                if new_child is entry:
                    return self
                new_entries = _replace(self.entries, idx, new_child)
                return _BitmapNode(self.bitmap, new_entries)
            existing_key, existing_value = entry
            if existing_key == key:
                if existing_value == value:
                    return self
                new_entries = _replace(self.entries, idx, (key, value))
                return _BitmapNode(self.bitmap, new_entries)
            existing_hash = _hash_of(existing_key)
            child = _create_node(
                existing_hash,
                existing_key,
                existing_value,
                h,
                shift + HASH_BITS,
                key,
                value,
            )
            new_entries = _replace(self.entries, idx, child)
            return _BitmapNode(self.bitmap, new_entries)
        new_bitmap = self.bitmap | bit
        new_entries = self.entries[:idx] + ((key, value),) + self.entries[idx:]
        return _BitmapNode(new_bitmap, new_entries)

    def delete(self, h: int, shift: int, key: Any) -> Union["_Node", None]:
        bit = 1 << _fragment(h, shift)
        if not self.bitmap & bit:
            return self
        idx = _popcount(self.bitmap & (bit - 1))
        entry = self.entries[idx]
        if isinstance(entry, _Node):
            new_child = entry.delete(h, shift + HASH_BITS, key)
            if new_child is entry:
                return self
            if new_child is None:
                return _shrink(self.bitmap, self.entries, idx, bit)
            new_entries = _replace(self.entries, idx, new_child)
            return _BitmapNode(self.bitmap, new_entries)
        existing_key, _ = entry
        if existing_key != key:
            return self
        return _shrink(self.bitmap, self.entries, idx, bit)

    def iter_entries(self) -> Iterator[Tuple[Any, Any]]:
        for entry in self.entries:
            if isinstance(entry, _Node):
                yield from entry.iter_entries()
            else:
                yield entry


class _CollisionNode(_Node):
    __slots__ = ("hash", "entries")

    def __init__(self, hash_: int, entries: tuple) -> None:
        self.hash = hash_
        self.entries = entries

    def get(self, h: int, shift: int, key: Any, nsv: Any) -> Any:
        for k, v in self.entries:
            if k == key:
                return v
        return nsv

    def set(self, h: int, shift: int, key: Any, value: Any) -> "_Node":
        for i, (k, v) in enumerate(self.entries):
            if k == key:
                if v == value:
                    return self
                return _CollisionNode(self.hash, _replace(self.entries, i, (key, value)))
        return _CollisionNode(self.hash, self.entries + ((key, value),))

    def delete(self, h: int, shift: int, key: Any) -> Union["_Node", None]:
        new_entries = tuple((k, v) for k, v in self.entries if k != key)
        if len(new_entries) == len(self.entries):
            return self
        if not new_entries:
            return None
        return _CollisionNode(self.hash, new_entries)

    def iter_entries(self) -> Iterator[Tuple[Any, Any]]:
        return iter(self.entries)


def _replace(entries: tuple, idx: int, value: Any) -> tuple:
    return entries[:idx] + (value,) + entries[idx + 1 :]


def _shrink(bitmap: int, entries: tuple, idx: int, bit: int) -> Union["_Node", None]:
    new_bitmap = bitmap & ~bit
    new_entries = entries[:idx] + entries[idx + 1 :]
    if new_bitmap == 0:
        return None
    return _BitmapNode(new_bitmap, new_entries)


def _create_node(
    hash1: int, k1: Any, v1: Any, hash2: int, shift: int, k2: Any, v2: Any
) -> _Node:
    if hash1 == hash2:
        return _CollisionNode(hash1, ((k1, v1), (k2, v2)))
    frag1, frag2 = _fragment(hash1, shift), _fragment(hash2, shift)
    if frag1 == frag2:
        child = _create_node(hash1, k1, v1, hash2, shift + HASH_BITS, k2, v2)
        return _BitmapNode(1 << frag1, (child,))
    entries = ((k1, v1), (k2, v2)) if frag1 < frag2 else ((k2, v2), (k1, v1))
    return _BitmapNode((1 << frag1) | (1 << frag2), entries)


class HAMT:
    """An immutable key/value trie: the persistent backing for `Map`/`Set`."""

    __slots__ = ("root", "size")

    def __init__(self, root: Union[_Node, None] = None, size: int = 0) -> None:
        self.root = root
        self.size = size

    def get(self, key: Any, nsv: Any = singleton) -> Any:
        if self.root is None:
            return nsv
        return self.root.get(_hash_of(key), 0, key, nsv)

    def set(self, key: Any, value: Any) -> "HAMT":
        h = _hash_of(key)
        if self.root is None:
            return HAMT(_BitmapNode(1 << _fragment(h, 0), ((key, value),)), 1)
        existed = self.root.get(h, 0, key, singleton) is not singleton
        new_root = self.root.set(h, 0, key, value)
        if new_root is self.root:
            return self
        return HAMT(new_root, self.size if existed else self.size + 1)

    def delete(self, key: Any) -> "HAMT":
        if self.root is None:
            return self
        new_root = self.root.delete(_hash_of(key), 0, key)
        if new_root is self.root:
            return self
        return HAMT(new_root, self.size - 1)

    def __len__(self) -> int:
        return self.size

    def __iter__(self) -> Iterator[Tuple[Any, Any]]:
        if self.root is None:
            return iter(())
        return self.root.iter_entries()


EMPTY = HAMT()
