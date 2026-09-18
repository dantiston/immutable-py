#!/usr/bin/env python3

from typing import Generic, Iterable, Iterator

from .collection import Indexed, ValueT
from .equality import singleton


class Stack(Indexed[ValueT], Generic[ValueT]):
    def __init__(self, items: Iterable[ValueT] = ()) -> None:
        self.items = list(items)

    @classmethod
    def of(cls, *items: ValueT) -> "Stack":
        return Stack(items) if items else _empty_stack

    @classmethod
    def is_stack(cls, other) -> bool:
        return isinstance(other, Stack)

    def get(self, index: int, nsv: ValueT = singleton) -> ValueT:
        try:
            return self.items[index]
        except IndexError as e:
            if nsv is singleton:
                raise e
            return nsv

    def peek(self, nsv: ValueT = singleton) -> ValueT:
        return self.first(nsv)

    def push(self, *values: ValueT) -> "Stack":
        if not values:
            return self
        # Sequential pushes each prepend to the front, so the last value
        # pushed ends up on top: push(1, 2, 3) leaves 3 on top, like
        # push(1) then push(2) then push(3) applied in order.
        return Stack(list(reversed(values)) + self.items[:])

    unshift = push

    def pop(self) -> "Stack":
        if not self.items:
            return self
        return Stack(self.items[1:])

    shift = pop

    def clear(self) -> "Stack":
        return _empty_stack

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[ValueT]:
        return iter(self.items)

    def __repr__(self) -> str:
        return f"Stack({self.items!r})"


_empty_stack = Stack()
