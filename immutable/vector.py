#!/usr/bin/env python3

"""A persistent vector trie (Clojure's PersistentVector / Immutable.js's List).

A 32-way branching trie gives O(log32 n) `get`/`set` at an arbitrary
index. A small "tail" buffer holding the last (<=32) elements gives O(1)
amortized `push`/`pop` at the end: most pushes just grow the tail; only
every 32nd push has to fold the full tail into the trie as a new leaf
(itself an O(log32 n) path-copy, since it recurses along one root-to-leaf
path).

This only supports efficient operations at *one* end (the end `push`/`pop`
work on). Arbitrary-index insert/delete and prepend are not backed by this
structure - `List`/`Stack` fall back to an O(n) rebuild for those, same as
they did with the previous plain-list backing.
"""

from typing import Any, Iterable, Iterator, Tuple, Union

BITS = 5
WIDTH = 1 << BITS
MASK = WIDTH - 1


def _tail_offset(count: int) -> int:
    if count < WIDTH:
        return 0
    return ((count - 1) >> BITS) << BITS


def _new_path(level: int, node: tuple) -> tuple:
    if level == 0:
        return node
    return (_new_path(level - BITS, node),)


def _push_tail(shift: int, node: tuple, tail_node: tuple, count: int) -> tuple:
    sub_idx = ((count - 1) >> shift) & MASK
    if shift == BITS:
        if sub_idx < len(node):
            return node[:sub_idx] + (tail_node,) + node[sub_idx + 1 :]
        return node + (tail_node,)
    if sub_idx < len(node):
        child = _push_tail(shift - BITS, node[sub_idx], tail_node, count)
        return node[:sub_idx] + (child,) + node[sub_idx + 1 :]
    return node + (_new_path(shift - BITS, tail_node),)


def _pop_tail(shift: int, node: tuple, count: int) -> Union[tuple, None]:
    sub_idx = ((count - 2) >> shift) & MASK
    if shift > BITS:
        new_child = _pop_tail(shift - BITS, node[sub_idx], count)
        if new_child is None and sub_idx == 0:
            return None
        if new_child is None:
            return node[:sub_idx]
        return node[:sub_idx] + (new_child,)
    if sub_idx == 0:
        return None
    return node[:sub_idx]


def _leaf_for(root: tuple, shift: int, index: int) -> tuple:
    node = root
    level = shift
    while level > 0:
        node = node[(index >> level) & MASK]
        level -= BITS
    return node


class Vector:
    """An immutable, structurally-shared sequence. See module docstring."""

    __slots__ = ("count", "shift", "root", "tail")

    def __init__(
        self, count: int = 0, shift: int = 0, root: Union[tuple, None] = None, tail: tuple = ()
    ) -> None:
        self.count = count
        self.shift = shift
        self.root = root
        self.tail = tail

    def __len__(self) -> int:
        return self.count

    def get(self, index: int) -> Any:
        if not 0 <= index < self.count:
            raise IndexError(index)
        if index >= _tail_offset(self.count):
            return self.tail[index & MASK]
        node = self.root
        for level in range(self.shift, 0, -BITS):
            node = node[(index >> level) & MASK]
        return node[index & MASK]

    def set(self, index: int, value: Any) -> "Vector":
        if not 0 <= index < self.count:
            raise IndexError(index)
        if index >= _tail_offset(self.count):
            new_tail = _replace(self.tail, index & MASK, value)
            return Vector(self.count, self.shift, self.root, new_tail)
        new_root = _set_in_trie(self.root, self.shift, index, value)
        return Vector(self.count, self.shift, new_root, self.tail)

    def push(self, value: Any) -> "Vector":
        if self.count - _tail_offset(self.count) < WIDTH:
            return Vector(self.count + 1, self.shift, self.root, self.tail + (value,))
        tail_node = self.tail
        if self.root is None:
            new_root, new_shift = tail_node, 0
        elif (self.count >> BITS) > (1 << self.shift):
            new_root = (self.root, _new_path(self.shift, tail_node))
            new_shift = self.shift + BITS
        else:
            new_root = _push_tail(self.shift, self.root, tail_node, self.count)
            new_shift = self.shift
        return Vector(self.count + 1, new_shift, new_root, (value,))

    def pop(self) -> "Vector":
        if self.count == 0:
            raise IndexError("pop from an empty Vector")
        if self.count == 1:
            return EMPTY
        if self.count - _tail_offset(self.count) > 1:
            return Vector(self.count - 1, self.shift, self.root, self.tail[:-1])
        new_tail = _leaf_for(self.root, self.shift, self.count - 2)
        if self.shift == 0:
            # The whole trie was a single leaf (no branching above it);
            # pulling it out as the new tail empties the trie entirely.
            new_root, new_shift = None, 0
        else:
            new_root = _pop_tail(self.shift, self.root, self.count)
            new_shift = self.shift
            if new_root is None:
                new_shift = 0
            elif self.shift > BITS and len(new_root) == 1:
                new_root, new_shift = new_root[0], self.shift - BITS
        return Vector(self.count - 1, new_shift, new_root, tuple(new_tail))

    def __iter__(self) -> Iterator[Any]:
        if self.root is not None:
            yield from _walk(self.root, self.shift)
        yield from self.tail

    @classmethod
    def from_iterable(cls, items: Iterable[Any]) -> "Vector":
        vector = EMPTY
        for item in items:
            vector = vector.push(item)
        return vector


def _walk(node: tuple, level: int) -> Iterator[Any]:
    if level == 0:
        yield from node
    else:
        for child in node:
            yield from _walk(child, level - BITS)


def _replace(entries: tuple, idx: int, value: Any) -> tuple:
    return entries[:idx] + (value,) + entries[idx + 1 :]


def _set_in_trie(node: tuple, shift: int, index: int, value: Any) -> tuple:
    if shift == 0:
        return _replace(node, index & MASK, value)
    sub_idx = (index >> shift) & MASK
    child = _set_in_trie(node[sub_idx], shift - BITS, index, value)
    return _replace(node, sub_idx, child)


EMPTY = Vector()
