#!/usr/bin/env python3

from typing import Iterable, Generic, Tuple, TypeVar, Union

KeyT = TypeVar('KeyT')
ValueT = TypeVar('ValueT')
NotSetValueT = TypeVar('NotSetValueT')

singleton = object()

class Collection(Generic[ValueT]):
    pass

class Sequence(Collection, Generic[ValueT]):
    pass

class List(Sequence, Generic[ValueT]):
    def __init__(self, items: Iterable[ValueT] = ()) -> None:
        self.items = list(items)

    @classmethod
    def of(cls, *items: Tuple[ValueT]) -> 'List':
        return List(items)

    @classmethod
    def is_list(cls, other) -> bool:
        return isinstance(other, List)

    def get(self, index: int) -> ValueT:
        return self.items[index]

    def has(self, index: int) -> bool:
        return index < len(self.items)

    def includes(self, value: ValueT) -> bool:
        return value in self.items

    def first(self, nsv: NotSetValueT = singleton) -> Union[ValueT, NotSetValueT]:
        try:
            return self.items[0]
        except IndexError as e:
            if nsv is singleton:
                raise e
            return nsv

    def last(self, nsv: NotSetValueT = singleton) -> Union[ValueT, NotSetValueT]:
        try:
            return self.items[-1]
        except IndexError as e:
            if nsv is singleton:
                raise e
            return nsv

    def delete(self, index: int) -> 'List':
        result = self.items[:]
        result.pop(index)
        return result

    def __len__(self) -> int:
        return len(self.items)

    def __contains__(self, value: ValueT) -> bool:
        return self.includes(value)
