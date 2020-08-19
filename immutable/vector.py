#!/usr/bin/env python3

"""
vector.py

A Persisent Vector implementation based on immutable.js and clojure.
"""

import copy

from dataclasses import dataclass
from typing import List, Iterator

from immutable import singleton

DEPTH = 5
WIDTH = 1 << DEPTH
MASK = WIDTH - 1


@dataclass
class Node(object):
    children: List['Node']

    def get(index: int, nsv) -> 'Node':
        self.children.get(index, nsv)

    def set(index: int, value) -> None:
        self.children[index] = value

class Vector(object):
    def __init__(self, length: int, shift: int, root: Node, tail: List):
        self.length = length
        self.shift = shift
        self.root = root
        self.tail = tail

    def __len__(self):
        return self.length

    def _tail_offset(self) -> int:
        if len(self) < WIDTH:
            return 0
        return ((len(self) - 1) >> DEPTH) << DEPTH

    def _get_values(self, index: int):
        if index >= self._tail_offset():
            return self.tail
        node = self.root
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

    def set(self, index: int, value):
        if index >= 0 and index < len(self):
            if index >= self._tail_offset():
                new_tail = list(self.tail)
                new_tail[index & MASK] = value
                return Vector(self.length, self.shift, self.root, new_tail)
            return Vector(
                self.length,
                self.shift,
                self._set(self.shift, self.root, index, value),
                self.tail,
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

    def add(self, value):
        if len(self) - self._tail_offset() < WIDTH:
            new_tail = [*self.tail, value]
            return Vector(self.length + 1, self.shift, self.root, new_tail)
        new_root = None
        new_shift = self.shift
        new_tail = Node(self.tail)
        if (len(self) >> DEPTH) > (1 << shift):
            new_root = Node(children=[root, self._new_path(shift, new_tail)])
            new_shift += DEPTH
        else:
            new_root = self._push_tail(self.shift, self.root, new_tail)
        return Vector(self.length + 1, new_shift, new_root, [value])

    def __iter__(self) -> Iterator:
        for i in range(len(self)):
            yield self.get(i)

    def asList(self) -> List:
        return list(self)

    def __repr__(self) -> str:
        return f"<Vector {repr(self.asList())}>"

    def __str__(self) -> str:
        return str(self.asList())

_empty_vector = Vector(0, 5, Node(children=[]), [])
