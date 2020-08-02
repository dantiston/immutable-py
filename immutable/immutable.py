#!/usr/bin/env python3

from typing import Iterable, Iterator, Callable, Generic, Tuple, TypeVar

KeyT = TypeVar('KeyT')
ValueT = TypeVar('ValueT')
ReturnT = TypeVar('ReturnT')

singleton = object()

class Collection(Generic[ValueT]):
    pass

class Indexed(Collection, Generic[ValueT]):

    def has(self, index: int) -> bool:
        return index < len(self)

    def first(self, nsv: ValueT = singleton) -> ValueT:
        return self.get(0, nsv)

    def last(self, nsv: ValueT = singleton) -> ValueT:
        return self.get(-1, nsv)

    def __contains__(self, value: ValueT) -> bool:
        return self.includes(value)

class List(Indexed, Generic[ValueT]):

    def __init__(self, items: Iterable[ValueT] = ()) -> None:
        self.items = list(items)

    @classmethod
    def of(cls, *items: Tuple[ValueT]) -> 'List':
        return List(items) if items else _empty_list

    @classmethod
    def is_list(cls, other) -> bool:
        return isinstance(other, List)

    def get(self, index: int, nsv: ValueT = singleton) -> ValueT:
        try:
            return self.items[index]
        except IndexError as e:
            if nsv is singleton:
                raise e
            return nsv

    def includes(self, value: ValueT) -> bool:
        return value in self.items

    def set(self, index: int, value: ValueT) -> 'List':
        result = self.items[:]
        result[index] = value
        return List(result)

    def delete(self, index: int) -> 'List':
        result = self.items[:]
        result.pop(index)
        return List(result)

    def insert(self, index: int, value: ValueT) -> 'List':
        result = self.items[:]
        result.insert(index, value)
        return List(result)

    def push(self, *values: Tuple[ValueT]) -> 'List':
        result = self.items[:]
        result.extend(values)
        return List(result)

    def pop(self, *values: Tuple[ValueT]) -> 'List':
        return self.delete(-1)

    def unshift(self, *values: Tuple[ValueT]) -> 'List':
        result = self.items[:]
        return List(list(values) + result)

    def shift(self, *values: Tuple[ValueT]) -> 'List':
        result = self.items[:]
        return List(result + list(values))

    def update(self, index: int, updater: Callable[[ValueT], ValueT], nsv: ValueT = singleton) -> 'List':
        return self.set(index, updater(self.get(index, nsv)))

    def update_all(self, updater: Callable[['List'], ReturnT]) -> ReturnT:
        return List(updater(self.items[:]))

    def clear(self) -> 'List':
        return _empty_list

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[ValueT]:
        return iter(self.items)


_empty_list = List()
