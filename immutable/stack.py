#!/usr/bin/env python3

from typing import Generic, Iterable, Iterator

from .collection import Indexed, ValueT
from .equality import singleton
from .vector import Vector


class Stack(Indexed[ValueT], Generic[ValueT]):
    # Internally stores elements in the reverse of front-to-back (stack)
    # order, so the "front" (top of stack) is always the *last* element of
    # the backing Vector - which is the end Vector's push/pop are O(1)
    # amortized for. This gets Stack's push/pop/peek onto the same trie
    # without needing a second, prepend-optimized structure.
    def __init__(self, items: Iterable[ValueT] = ()) -> None:
        self._vector = Vector.from_iterable(reversed(tuple(items)))

    @classmethod
    def _wrap(cls, vector: Vector) -> "Stack":
        instance = cls.__new__(cls)
        instance._vector = vector
        return instance

    @classmethod
    def of(cls, *items: ValueT) -> "Stack":
        return Stack(items) if items else _empty_stack

    @classmethod
    def is_stack(cls, other) -> bool:
        return isinstance(other, Stack)

    def get(self, index: int, nsv: ValueT = singleton) -> ValueT:
        n = len(self._vector)
        if index < 0:
            index += n
        try:
            return self._vector.get(n - 1 - index)
        except IndexError:
            if nsv is singleton:
                raise
            return nsv

    def peek(self, nsv: ValueT = singleton) -> ValueT:
        return self.first(nsv)

    def push(self, *values: ValueT) -> "Stack":
        if not values:
            return self
        # Sequential pushes each prepend to the front, so the last value
        # pushed ends up on top: push(1, 2, 3) leaves 3 on top, like
        # push(1) then push(2) then push(3) applied in order. That's
        # exactly appending to the reverse-order backing Vector.
        vector = self._vector
        for value in values:
            vector = vector.push(value)
        return Stack._wrap(vector)

    unshift = push

    def pop(self) -> "Stack":
        if not self._vector:
            return self
        return Stack._wrap(self._vector.pop())

    shift = pop

    def clear(self) -> "Stack":
        return _empty_stack

    def __len__(self) -> int:
        return len(self._vector)

    def __iter__(self) -> Iterator[ValueT]:
        return reversed(list(self._vector))

    def __repr__(self) -> str:
        return f"Stack({list(self)!r})"


_empty_stack = Stack()
