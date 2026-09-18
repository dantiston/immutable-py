# Roadmap

A phased plan to bring immutable.py to parity with [Immutable.js][]. Phases are
ordered by dependency, not necessarily by priority — later phases assume the
abstractions built in earlier ones.

[Immutable.js]: https://github.com/immutable-js/immutable-js

## Current state (as of this plan)

- `List` exists, backed by a plain Python `list` copied on every write (not a
  persistent vector trie). Implements: `of`, `is_list`, `get`, `includes`,
  `set`, `delete`, `insert`, `push`, `pop`, `unshift`, `shift`, `update`,
  `thru`, `clear`, `concat`, `map`, `is_empty`, `__len__`, `__iter__`.
- `Collection` / `Indexed` base classes exist with `has`, `first`, `last`,
  `__contains__`.
- No `Map`, `Set`, `OrderedMap`, `OrderedSet`, `Stack`, `Record`, `Seq`,
  `Range`, `Repeat`.
- No shared iteration/functional mixin (`filter`, `reduce`, `sort`, `find`,
  `groupBy`, `flatMap`, `slice`/`take`/`skip` family, etc.) — each type would
  otherwise reimplement these.
- No equality/hashing protocol (`is()`, `hash()`), no `fromJS`/`toJS`.
- Tests: `unittest`, decent coverage of `List`'s current methods. No CI, no
  packaging, no type checking.

## Phase 0 — Project infrastructure

Do this first so every later phase lands on a repo that can catch regressions.

- [ ] Add `pyproject.toml` (build metadata, replaces bare `requirements.txt`).
- [ ] Switch dev tooling to `pytest` (keep `unittest.TestCase` compatibility,
      tests don't need rewriting).
- [ ] Add `mypy` (or `pyright`) config and start enforcing it on `immutable/`.
- [ ] Add GitHub Actions CI: lint (`black --check`), type-check, test on a
      matrix of supported Python versions.
- [ ] Pin/upgrade `black` (19.10b0 predates modern Python syntax support).
- [ ] Decide minimum supported Python version (drives whether `functools`
      `singledispatch`, structural pattern matching, etc. are usable).

## Phase 1 — Core abstractions

Immutable.js's real power is that every collection shares one functional
surface (`Collection.prototype`) and a value-equality protocol. Build that
once, mix it into every concrete type later, instead of re-deriving it per
type.

- [ ] Design `Seq` / `Collection` class hierarchy mirroring `Collection.Keyed`,
      `Collection.Indexed`, `Collection.Set` — an ABC per shape, not just the
      current flat `Collection`/`Indexed` split.
- [ ] Implement the shared functional mixin (applies to `List`, `Map`, `Set`,
      `Stack`, `Seq`, etc.):
      `map`, `filter`, `filterNot`, `reduce`, `reduceRight`, `find`,
      `findLast`, `forEach`, `some`/`any`, `every`/`all`, `join`, `reverse`,
      `sort`, `sortBy`, `groupBy`, `partition`, `flatten`, `flatMap`, `min`,
      `max`, `minBy`, `maxBy`, `count`, `countBy`, `slice`, `take`,
      `takeLast`, `takeWhile`, `takeUntil`, `skip`, `skipLast`, `skipWhile`,
      `skipUntil`, `entries`/`keys`/`values` iterators, `toArray`/`toList`/
      `toMap`/`toSet`/`toSeq`/`toJS`.
      (Rename JS-style names to Pythonic ones deliberately — see Phase 8.)
- [ ] Implement `is(a, b)`: immutable equality — identity fast path, NaN
      handling, deep structural equality via each collection's `.equals()`.
- [ ] Implement `hash(value)` and a `__hash__`/`__eq__` convention every
      persistent collection follows, so collections can nest as `Map`/`Set`
      keys (this is the one place Python's built-in hashing isn't enough,
      since values need *structural* hashing, not identity).
- [ ] Decide the `nsv` (not-set-value)/sentinel convention project-wide
      (`List` already uses `singleton`) and apply it consistently.

## Phase 2 — Finish `List`

Close out the type that's already started before moving on.

- [ ] Rebuild `List` on top of the Phase 1 base classes/mixin instead of
      ad hoc methods.
- [ ] Fill remaining gaps against Immutable.js's `List`: `setSize`,
      `withMutations`/`asMutable`/`asImmutable`, `equals`, `hashCode`,
      `toString`, `slice`, `wasAltered` (if mutation batching is
      implemented — see Phase 9).
- [ ] Fix known correctness gaps: `pop()`/`unshift()`/`shift()` currently
      ignore or misuse their `*values` parameters; `set`/`insert`/`delete`
      don't bounds-check or support negative indices the way Immutable.js
      does; `map`'s signature (`updater(self.items[:])`) doesn't match
      Immutable.js's per-element `(value, index, iter) => value` callback.
- [ ] Expand `tests/test_immutable.py` coverage to match.

## Phase 3 — `Map` / `OrderedMap`

- [ ] `Map`: `get`, `set`, `has`, `delete`/`remove`, `update`, `updateIn`,
      `getIn`, `setIn`, `deleteIn`, `merge`, `mergeWith`, `mergeDeep`,
      `mergeDeepWith`, `map`, `filter`, `flip`, `withMutations`.
- [ ] `OrderedMap`: same surface, insertion order preserved on iteration.
- [ ] Key equality must go through the Phase 1 `is`/`hash` protocol, not
      Python's raw `==`/`hash()`, so nested immutable collections work as
      keys the way they do in Immutable.js.

## Phase 4 — `Set` / `OrderedSet`

- [ ] `Set`: `add`, `remove`/`delete`, `union`, `intersect`, `subtract`,
      `isSubset`, `isSuperset`, `merge`.
- [ ] `OrderedSet`: same, insertion order preserved.

## Phase 5 — `Stack`

- [ ] `push`, `pop`, `peek`, `unshift`/`shift` aliases, `clear`.

## Phase 6 — `Record`

- [ ] Factory (`Record(defaultValues, name)`) producing a record class with
      fixed keys, default values, attribute-style access, and immutable
      `set`/`update`/`merge`. This is architecturally different from the
      other types (schema-fixed) and worth its own design pass.

## Phase 7 — `Seq`, `Range`, `Repeat`

- [ ] `Seq` (lazy): `Seq.Indexed`, `Seq.Keyed`, `Seq.Set` wrapping
      iterables/generators without eagerly materializing — this is where
      Python generators map naturally onto Immutable.js's laziness.
- [ ] `Range(start, end, step)`, `Repeat(value, times)` as lazy `Seq`
      subclasses.
- [ ] Make sure the Phase 1 mixin methods stay lazy on `Seq` (return new
      `Seq`s) but eager on concrete collections (return concrete
      collections), matching Immutable.js's distinction.

## Phase 8 — Top-level API surface & Pythonization

- [ ] Module-level factory functions: `List()`, `Map()`, `Set()`, `Stack()`,
      `fromJS()`/`from_js()`, `is_()`(`is` is a Python keyword — needs a
      naming decision), `hash_()`.
- [ ] Deliberate naming pass: decide once, in `ROADMAP.md` or a
      `STYLE.md`, whether the public API uses `camelCase` (matches
      Immutable.js, eases porting docs/examples) or `snake_case` (matches
      PEP 8, matches what `List` already does — e.g. `is_list`, `is_empty`).
      `List` currently already leans snake_case; apply that consistently
      project-wide rather than deciding per-type.
- [ ] `__repr__`/`__str__` matching Immutable.js's `toString()` output
      conventions, adapted to Python idiom.

## Phase 9 — Performance: real persistent structures

The current `List` copies its backing Python list on every write — O(n) per
op instead of Immutable.js's O(log32 n). This is fine for correctness and
early API work, but should be treated as a deliberate, documented tradeoff,
not the final implementation.

- [ ] Implement a persistent vector trie (32-way branching, like
      Immutable.js) for `List`/`Stack`.
- [ ] Implement a HAMT (hash array mapped trie) for `Map`/`Set`.
- [ ] Add `withMutations`/transient-batch support once the trie exists, so
      bulk updates avoid the per-op allocation overhead entirely.
- [ ] Add benchmarks (`asv` or a simple `pytest-benchmark` suite) comparing
      naive-copy vs. trie-backed implementations, so this phase has a
      measurable "done."

## Phase 10 — Docs & examples

- [ ] Per-type README section (or Sphinx/mkdocs site) with runnable
      examples, mirroring Immutable.js's docs structure.
- [ ] Docstrings on every public method.
- [ ] A migration note for JS developers: naming differences from Phase 8,
      what's intentionally not ported (e.g. JS-specific interop like
      `toJSON`), what's Python-idiomatic instead (`__iter__`, `__len__`,
      `__contains__`, `__getitem__` already partially done).

## Phase 11 — Packaging & release

- [ ] `pyproject.toml` build backend, versioning scheme, `CHANGELOG.md`.
- [ ] Publish to PyPI, tag `v0.1.0` once Phases 0–5 (core collections) are
      solid, even before `Seq`/performance work lands — ship the usable
      subset early rather than gating release on 100% parity.

## Suggested sequencing

Phases 0–2 are the near-term, concrete next steps (infra, then the shared
base classes, then finishing `List` on top of them). Phases 3–6 (`Map`,
`Set`, `Stack`, `Record`) can proceed in roughly that order of usefulness —
`Map` unlocks the most downstream value. `Seq`/`Range`/`Repeat` (Phase 7) and
the trie rewrite (Phase 9) are the two phases most worth deferring: both are
substantial, and the eager/copying implementations from earlier phases are a
legitimate v0.1 to ship and get feedback on first.
