# immutable.py API guide

This document is both the API reference and a test suite: every `>>>`
example below is executed by `doctest` (see [Running this file](#running-this-file)
at the bottom), so the examples are guaranteed to match the library's
actual behavior — if they ever drift apart, the test suite fails.

Every method here returns a **new** collection; the original is never
modified. That's the one rule underlying everything below:

```pycon
>>> import immutable
>>> original = immutable.List((1, 2, 3))
>>> changed = original.push(4)
>>> list(original)
[1, 2, 3]
>>> list(changed)
[1, 2, 3, 4]

```

## Contents

- [List](#list)
- [Stack](#stack)
- [Map and OrderedMap](#map-and-orderedmap)
- [Set and OrderedSet](#set-and-orderedset)
- [The shared functional API](#the-shared-functional-api)
- [Equality and hashing](#equality-and-hashing)
- [A note on Map/Set iteration order](#a-note-on-mapset-iteration-order)
- [Running this file](#running-this-file)

## List

`List` is an ordered, indexed sequence, backed by a persistent vector trie
(see `immutable/vector.py`) — `get`/`set` are O(log32 n), and `push`/`pop`
at the end are O(1) amortized.

```pycon
>>> a = immutable.List((1, 2, 3))
>>> a
List([1, 2, 3])

```

Building one: the constructor takes any iterable, and `List.of(...)` takes
its arguments directly:

```pycon
>>> immutable.List([1, 2, 3]) == immutable.List((1, 2, 3)) == immutable.List.of(1, 2, 3)
True
>>> immutable.List()
List([])
>>> immutable.List.is_list(a)
True
>>> immutable.List.is_list([1, 2, 3])
False

```

Reading: `get` (with an optional not-set-value for out-of-range access,
otherwise it raises), `first`/`last`, `includes`/`in`:

```pycon
>>> a.get(1)
2
>>> a.get(10, "n/a")
'n/a'
>>> a.get(10)
Traceback (most recent call last):
    ...
IndexError: 10
>>> a.first()
1
>>> a.last()
3
>>> a.includes(2)
True
>>> 2 in a
True

```

Negative indices count from the end, same as a Python list:

```pycon
>>> a.get(-1)
3

```

Writing — each of these returns a new `List`, leaving `a` untouched.
`set` past the current end auto-extends with `None`, matching
Immutable.js:

```pycon
>>> a.set(1, 99)
List([1, 99, 3])
>>> a.set(5, "z")
List([1, 2, 3, None, None, 'z'])
>>> a.delete(1)
List([1, 3])
>>> a.delete(99) is a
True
>>> a.insert(1, 99)
List([1, 99, 2, 3])
>>> a.push(4, 5)
List([1, 2, 3, 4, 5])
>>> a.pop()
List([1, 2])
>>> a.unshift(0)
List([0, 1, 2, 3])
>>> a.shift()
List([2, 3])
>>> a.update(0, lambda x: x * 10)
List([10, 2, 3])
>>> a.set_size(5)
List([1, 2, 3, None, None])
>>> a.set_size(1)
List([1])
>>> a.clear()
List([])

```

`concat` accepts a mix of scalars and iterables (including other `List`s),
flattening one level:

```pycon
>>> a.concat([4, 5], 6, immutable.List((7, 8)))
List([1, 2, 3, 4, 5, 6, 7, 8])

```

`thru` runs an arbitrary function over the whole `List` and returns
whatever it returns — a general-purpose escape hatch:

```pycon
>>> a.thru(sum)
6

```

`List` supports `len`, iteration, and value equality (two `List`s with the
same elements in the same order are equal, regardless of whether they're
the same object):

```pycon
>>> len(a)
3
>>> list(a)
[1, 2, 3]
>>> a == immutable.List((1, 2, 3))
True
>>> a == immutable.List((1, 2, 4))
False

```

## Stack

`Stack` is a LIFO structure: `push`/`pop`/`peek` all operate on the
*front*. It shares `List`'s trie (internally storing elements in reverse,
so its hot end lines up with the trie's efficient end) and the same
`Indexed` base, so `get`, `first`/`last`, `includes`, equality, and the
whole shared functional API (below) all work the same way.

```pycon
>>> s = immutable.Stack((1, 2, 3))
>>> s
Stack([1, 2, 3])
>>> s.peek()
1

```

Pushing multiple values at once behaves like pushing them one at a time,
in order — so the *last* argument ends up on top:

```pycon
>>> s.push(4, 5, 6)
Stack([6, 5, 4, 1, 2, 3])
>>> s.push(4, 5, 6).peek()
6
>>> s.pop()
Stack([2, 3])
>>> s.clear()
Stack([])

```

`unshift`/`shift` are aliases for `push`/`pop` (Immutable.js's `Stack`
treats them as synonyms, since "front" is the only end that matters):

```pycon
>>> s.unshift(0) == s.push(0)
True
>>> s.shift() == s.pop()
True

```

`Stack.of(...)`, `Stack.is_stack(...)`, and an empty `pop`/no-match `peek`
behave the same way as `List`'s equivalents:

```pycon
>>> immutable.Stack.of(1, 2, 3)
Stack([1, 2, 3])
>>> empty = immutable.Stack()
>>> empty.pop() is empty
True
>>> empty.peek("none")
'none'

```

## Map and OrderedMap

`Map` is a persistent hash map backed by a HAMT (see `immutable/hamt.py`):
`get`/`set`/`delete` are O(log32 n), with structural sharing so old
versions stay valid and cheap to keep around.

```pycon
>>> m = immutable.Map({"a": 1, "b": 2})
>>> m.get("a")
1
>>> m.get("z", 0)
0
>>> m.has("a")
True
>>> "a" in m
True

```

`get` with no not-set-value raises, like a plain `dict`:

```pycon
>>> immutable.Map().get("missing")
Traceback (most recent call last):
    ...
KeyError: 'missing'

```

Writing returns a new `Map`; `delete` on a missing key is a no-op that
returns the same object:

```pycon
>>> sorted(m.set("c", 3).to_dict().items())
[('a', 1), ('b', 2), ('c', 3)]
>>> sorted(m.delete("a").to_dict().items())
[('b', 2)]
>>> m.delete("missing") is m
True

```

`update` applies a function to the current value (or a not-set-value,
`None` by default, if the key is absent) and stores the result:

```pycon
>>> m.update("a", lambda v: v + 10).get("a")
11
>>> m.update("z", lambda v: (v or 0) + 1).get("z")
1

```

`flip` swaps keys and values; `merge`/`merge_with`/`merge_deep` combine
maps (`merge_with` takes a conflict-resolution function, `merge_deep`
recurses into nested `Map` values):

```pycon
>>> sorted(m.flip().to_dict().items())
[(1, 'a'), (2, 'b')]
>>> sorted(m.merge({"b": 20, "c": 3}).to_dict().items())
[('a', 1), ('b', 20), ('c', 3)]
>>> sorted(m.merge_with(lambda old, new: old + new, {"a": 10}).to_dict().items())
[('a', 11), ('b', 2)]
>>> nested = immutable.Map({"a": immutable.Map({"x": 1})})
>>> other = immutable.Map({"a": immutable.Map({"y": 2})})
>>> sorted(nested.merge_deep(other).get("a").to_dict().items())
[('x', 1), ('y', 2)]

```

`get_in`/`set_in`/`update_in`/`delete_in` walk a path of keys/indices
through nested `Map`s (and `List`s, and plain `dict`s/`list`s), the same
way Immutable.js's do. `set_in`/`update_in` create intermediate `Map`s
along the path if they don't already exist:

```pycon
>>> deep = immutable.Map({"a": immutable.Map({"b": immutable.List((1, 2, 3))})})
>>> deep.get_in(["a", "b", 1])
2
>>> immutable.Map().get_in(["a", "b"], "default")
'default'
>>> immutable.Map().set_in(["a", "b"], 1).get_in(["a", "b"])
1
>>> counters = immutable.Map({"a": immutable.Map({"count": 1})})
>>> counters.update_in(["a", "count"], lambda x: x + 1).get_in(["a", "count"])
2
>>> sorted(
...     immutable.Map({"a": immutable.Map({"b": 1, "c": 2})})
...     .delete_in(["a", "b"])
...     .get_in(["a"])
...     .to_dict()
...     .items()
... )
[('c', 2)]

```

`len`, `Map.is_map`, and value equality (order-independent — two `Map`s
with the same key/value pairs are equal regardless of insertion order):

```pycon
>>> len(m)
2
>>> immutable.Map.is_map(m)
True
>>> m == immutable.Map({"b": 2, "a": 1})
True

```

**`OrderedMap`** has the exact same API, but additionally guarantees
iteration in insertion order — re-`set`-ing an existing key updates its
value without moving its position, just like a Python `dict`:

```pycon
>>> om = immutable.OrderedMap([("z", 1), ("a", 2), ("m", 3)])
>>> list(om.keys())
['z', 'a', 'm']
>>> list(om.set("z", 100).entries())
[('z', 100), ('a', 2), ('m', 3)]
>>> list(om.delete("a").keys())
['z', 'm']
>>> immutable.OrderedMap.is_ordered_map(om)
True
>>> immutable.Map.is_map(om)
True

```

## Set and OrderedSet

`Set` is a persistent hash set, also HAMT-backed, with the usual set
algebra:

```pycon
>>> s2 = immutable.Set([1, 2, 3])
>>> s2.has(2)
True
>>> 2 in s2
True
>>> sorted(s2.add(4))
[1, 2, 3, 4]
>>> s2.add(2) is s2
True
>>> sorted(s2.delete(2))
[1, 3]
>>> s2.delete(99) is s2
True

```

```pycon
>>> sorted(s2.union([3, 4, 5]))
[1, 2, 3, 4, 5]
>>> sorted(s2.intersect([2, 3, 4]))
[2, 3]
>>> sorted(s2.subtract([2]))
[1, 3]
>>> s2.is_subset([1, 2, 3, 4])
True
>>> s2.is_superset([1, 2])
True

```

```pycon
>>> len(s2)
3
>>> immutable.Set.is_set(s2)
True
>>> immutable.Set.of(1, 2, 3) == s2
True
>>> s2 == immutable.Set([3, 2, 1])
True

```

**`OrderedSet`** again adds an insertion-order guarantee on top of the
same API:

```pycon
>>> oset = immutable.OrderedSet(["z", "a", "m"])
>>> list(oset)
['z', 'a', 'm']
>>> list(oset.add("z")), oset.add("z") is oset
(['z', 'a', 'm'], True)
>>> list(oset.delete("a"))
['z', 'm']
>>> immutable.OrderedSet.is_ordered_set(oset)
True

```

## The shared functional API

`List`, `Stack`, `Map`, `Set`, and their `Ordered*` variants all share one
functional surface, implemented once in `immutable/collection.py` and
mixed into every concrete type. On `List`/`Stack` it operates on values in
order; on `Map` it operates on values (keeping the associated keys); on
`Set` it operates on elements. The examples below mostly use `List` since
it reads the most naturally, with a couple of `Map` examples to show the
key-preserving behavior.

```pycon
>>> nums = immutable.List((5, 3, 8, 1, 9, 2))

```

Transforming — `map`, `filter`, `filter_not`:

```pycon
>>> nums.map(lambda x: x * 2)
List([10, 6, 16, 2, 18, 4])
>>> nums.filter(lambda x: x > 3)
List([5, 8, 9])
>>> nums.filter_not(lambda x: x > 3)
List([3, 1, 2])

```

Reducing — `reduce`, `reduce_right` (with an optional initial value):

```pycon
>>> nums.reduce(lambda acc, x: acc + x)
28
>>> nums.reduce(lambda acc, x: acc + x, 100)
128
>>> nums.reduce_right(lambda acc, x: str(acc) + str(x))
'291835'

```

Searching — `find`/`find_last` (raise if nothing matches and no
not-set-value is given, like `get`), `some`/`every`:

```pycon
>>> nums.find(lambda x: x > 5)
8
>>> nums.find_last(lambda x: x > 3)
9
>>> nums.find(lambda x: x > 100)
Traceback (most recent call last):
    ...
ValueError: find: no matching value
>>> nums.some(lambda x: x > 8)
True
>>> nums.every(lambda x: x > 0)
True

```

Counting — `count`, `count_by`, `min`/`max`/`min_by`/`max_by`:

```pycon
>>> nums.count()
6
>>> nums.count(lambda x: x > 3)
3
>>> dict(sorted(nums.count_by(lambda x: x % 2).items()))
{0: 2, 1: 4}
>>> nums.min(), nums.max()
(1, 9)
>>> nums.min_by(lambda x: -x), nums.max_by(lambda x: -x)
(9, 1)

```

Reordering and grouping — `sort`, `sort_by`, `reverse`, `group_by`,
`partition`:

```pycon
>>> nums.sort()
List([1, 2, 3, 5, 8, 9])
>>> nums.sort(reverse=True)
List([9, 8, 5, 3, 2, 1])
>>> nums.sort_by(lambda x: -x)
List([9, 8, 5, 3, 2, 1])
>>> nums.reverse()
List([2, 9, 1, 8, 3, 5])
>>> groups = nums.group_by(lambda x: x % 2)
>>> {key: list(group) for key, group in sorted(groups.items())}
{0: [8, 2], 1: [5, 3, 1, 9]}
>>> falsy, truthy = nums.partition(lambda x: x > 4)
>>> list(falsy), list(truthy)
([3, 1, 2], [5, 8, 9])

```

Windowing — `slice`, `take`/`take_last`/`take_while`/`take_until`,
`skip`/`skip_last`/`skip_while`/`skip_until`:

```pycon
>>> nums.slice(1, 4)
List([3, 8, 1])
>>> nums.take(3)
List([5, 3, 8])
>>> nums.take_last(2)
List([9, 2])
>>> nums.take_while(lambda x: x < 8)
List([5, 3])
>>> nums.take_until(lambda x: x > 5)
List([5, 3])
>>> nums.skip(2)
List([8, 1, 9, 2])
>>> nums.skip_last(2)
List([5, 3, 8, 1])
>>> nums.skip_while(lambda x: x < 8)
List([8, 1, 9, 2])
>>> nums.skip_until(lambda x: x > 5)
List([8, 1, 9, 2])

```

Converting out — `join`, `to_list`, `to_set`, `is_empty`:

```pycon
>>> nums.join()
'5,3,8,1,9,2'
>>> nums.join(" - ")
'5 - 3 - 8 - 1 - 9 - 2'
>>> nums.to_list()
[5, 3, 8, 1, 9, 2]
>>> sorted(nums.to_set())
[1, 2, 3, 5, 8, 9]
>>> nums.is_empty(), immutable.List().is_empty()
(False, True)

```

The same methods on `Map` operate on values but preserve key
associations:

```pycon
>>> prices = immutable.Map({"a": 1, "b": 2, "c": 3})
>>> sorted(prices.map(lambda v: v * 10).to_dict().items())
[('a', 10), ('b', 20), ('c', 30)]
>>> sorted(prices.filter(lambda v: v > 1).to_dict().items())
[('b', 2), ('c', 3)]
>>> prices.reduce(lambda acc, v: acc + v, 0)
6

```

## Equality and hashing

`is_(a, b)` mirrors Immutable.js's `is()`: identity first, then
NaN-equals-NaN (unlike `==`, where `nan != nan`), then falls back to `==`
— which every collection here overrides to mean deep structural equality:

```pycon
>>> nan = float("nan")
>>> nan == nan
False
>>> immutable.is_(nan, nan)
True
>>> immutable.is_(immutable.List((1, 2)), immutable.List((1, 2)))
True

```

`hash_(value)` is a thin wrapper over the builtin `hash()`; every
collection here defines `__hash__` structurally (based on shape and
contents, not identity), so they can nest as `Map`/`Set` keys and values:

```pycon
>>> immutable.hash_("x") == hash("x")
True
>>> hash(immutable.List((1, 2))) == hash(immutable.List((1, 2)))
True
>>> inner = immutable.List((1, 2))
>>> keyed_by_list = immutable.Map({inner: "found it"})
>>> keyed_by_list.get(immutable.List((1, 2)))
'found it'

```

## A note on Map/Set iteration order

`Map` and `Set` iterate in **hash-bucket order**, not insertion order —
this matches Immutable.js's actual (unordered) `Map`/`Set` semantics, and
falls straight out of being HAMT-backed rather than `dict`-backed. Two
`Map`s (or `Set`s) built from the same pairs in a different order are
still equal, but printing or iterating them directly isn't guaranteed to
come out in the order you built them:

```pycon
>>> immutable.Map({"a": 1, "b": 2}) == immutable.Map({"b": 2, "a": 1})
True

```

When you need a stable, predictable iteration order, either use
`OrderedMap`/`OrderedSet` (which track insertion order explicitly), or
sort the output yourself, as most of the examples above do with
`sorted(...)`.

## Running this file

```
python -m unittest discover -s tests
```

runs this file as part of the normal test suite (via `tests/test_doctest.py`,
which registers it with `doctest.DocFileSuite`). To run just the examples
in this file directly:

```
python -m doctest API.md
```

(no output means everything passed).
