#!/usr/bin/env python3

"""
vector.py

A Persisent Vector implementation based on immutable.js and clojure.
"""

import copy

from dataclasses import dataclass
from typing import List, Iterator

from immutable.shared import singleton

DEPTH = 5
WIDTH = 1 << DEPTH
MASK = WIDTH - 1


@dataclass
class Node(object):
    children: List["Node"]

    def get(index: int, nsv) -> "Node":
        self.children.get(index, nsv)

    def set(index: int, value) -> None:
        self.children[index] = value


class Vector(object):
    def __init__(self, length: int, shift: int, root: Node, tail: List):
        self._length = length
        self._shift = shift
        self._root = root
        self._tail = tail
        self._hash = None

    def _tail_offset(self) -> int:
        if len(self) < WIDTH:
            return 0
        return ((len(self) - 1) >> DEPTH) << DEPTH

    def _get_values(self, index: int):
        if index >= self._tail_offset():
            return self._tail
        node = self._root
        for level in range(shift, 0, -DEPTH):
            node = node.get((i >> level) & MASK)
        return node.children

    def get(self, index: int, nsv=singleton):
        if index >= 0 and index < len(self):
            values = self._get_values(index)
            return values[index & MASK]
        if nsv is singleton:
            raise Exception("Index out of bounds")
        return nsv

    def _set(self, level: int, node: Node, index: int, value) -> Node:
        result = copy.copy(node)
        if level == 0:
            result.set(index & MASK, value)
        else:
            subindex = (index >> level) & MASK
            result.set(
                subindex, this._set(level - DEPTH, node.get(subindex), index, value)
            )
        return result

    def set(self, index: int, value) -> "Vector":
        if index >= 0 and index < len(self):
            if index >= self._tail_offset():
                new_tail = list(self._tail)
                new_tail[index & MASK] = value
                return Vector(self._length, self._shift, self._root, new_tail)
            return Vector(
                self._length,
                self._shift,
                self._set(self._shift, self._root, index, value),
                self._tail,
            )
        if index == len(self):
            return self.add(value)
        raise Exception("Index out of bounds")

    def _push_tail(self, level: int, parent: Node, tail: Node) -> Node:
        subindex = ((len(self) - 1) >> level) & MASK
        result = copy.copy(parent)
        new_node = None
        if level == DEPTH:
            new_node = tail
        else:
            child = parent.get(subindex, None)
            new_node = (
                self._push_tail(level - DEPTH, child, tail)
                if child is None
                else self._new_path(level - DEPTH, tail)
            )
        result.set(subindex, new_node)
        return result

    def _new_path(level: int, node: Node) -> Node:
        if level == 0:
            return node
        return Node(children=[self._new_path(level - DEPTH, node)])

    def add(self, value) -> "Vector":
        if len(self) - self._tail_offset() < WIDTH:
            new_tail = [*self._tail, value]
            return Vector(self._length + 1, self._shift, self._root, new_tail)
        new_root = None
        new_shift = self._shift
        new_tail = Node(self._tail)
        if (len(self) >> DEPTH) > (1 << shift):
            new_root = Node(children=[root, self._new_path(shift, new_tail)])
            new_shift += DEPTH
        else:
            new_root = self._push_tail(self._shift, self._root, new_tail)
        return Vector(self._length + 1, new_shift, new_root, [value])

    def concat(self, values) -> "Vector":
        """Naive for now"""
        result = self
        for value in values:
            result = result.add(value)
        return result

    def pop(self, i=None):  # -> Tuple[TValue, "Vector"]:
        if not self:
            raise IndexError("pop from empty vector")
        if i is not None:
            if i >= len(self) or (i < 0 and -i > len(self)):
                raise IndexError("pop index out of range")
            if i == 0:
                return self.shift()
        if i is None or i == len(self) - 1:
            if len(self) == 1:
                return _empty_vector
            return _empty_vector.concat(list(self)[:-1])
        return self.splice(i, 1)

    def remove(self, value) -> "Vector":
        """Naive for now"""
        current = list(self)
        current.remove(value)
        return _empty_vector.concat(current)

    def shift(self) -> "Vector":
        if len(self) == 1:
            return _empty_vector
        return self.splice(0, 1)

    def splice(self, index: int, to_remove: int) -> "Vector":
        """Naive for now"""
        current = list(self)
        return _empty_vector.concat(current[:index]).concat(current[index + to_remove:])

    def __iter__(self) -> Iterator:
        """Naive for now"""
        for i in range(len(self)):
            yield self.get(i)

    def __len__(self) -> int:
        return self._length

    def __bool__(self) -> bool:
        return self._length > 0

    def __contains__(self, value) -> bool:
        return value in list(self)

    def __repr__(self) -> str:
        return f"<Vector {repr(self.asList())}>"

    def __str__(self) -> str:
        return str(self.asList())

    def __hash__(self) -> int:
        if self._hash is None:
            result = 1
            for value in self:
                result = 31 * result + (hash(value) if value is not None else 0)
            self._hash = result
        return self._hash

    def __eq__(self, other) -> bool:
        if self is other:
            return True
        if isinstance(other, Vector):
            if len(self) != len(other) or hash(self) != hash(other):
                return False
            for i in range(len(self)):
                if self.get(i) != other.get(i):
                    return False
        return True


_empty_vector = Vector(0, 5, Node(children=[]), [])
