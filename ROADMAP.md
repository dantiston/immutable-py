# Roadmap

A phased plan to bring immutable.py to parity with [Immutable.js][]. Phases are
ordered by dependency, not necessarily by priority — later phases assume the
abstractions built in earlier ones.

[Immutable.js]: https://github.com/immutable-js/immutable-js

## Current state (as of this plan)

Phases 1–5 below are done: `immutable/collection.py` has a shared
`Collection`/`Indexed`/`Keyed`/`SetCollection` base implementing the
functional mixin once and an `is_()`/`hash_()` equality protocol
(`immutable/equality.py`), and `List`, `Stack`, `Map`/`OrderedMap`, and
`Set`/`OrderedSet` are all built on top of it (`immutable/list.py`,
`stack.py`, `map.py`, `set.py`). 123 tests pass (`python -m unittest
discover -s tests`). Still missing: `Record`, `Seq`/`Range`/`Repeat`,
`fromJS`/`toJS`, `flatten`/`flatMap`, `with_mutations`/transient batching,
the real trie-backed performance layer, and all of Phase 0 (CI, packaging,
type checking). See the per-phase notes below for exactly what shipped vs.
what's still open in each.

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

- [x] Design `Seq` / `Collection` class hierarchy mirroring `Collection.Keyed`,
      `Collection.Indexed`, `Collection.Set` — done as `Indexed`, `Keyed`,
      `SetCollection` in `immutable/collection.py` (no lazy `Seq` yet — see
      Phase 7).
- [x] Implement the shared functional mixin (applies to `List`, `Map`, `Set`,
      `Stack`): `map`, `filter`, `filter_not`, `reduce`, `reduce_right`,
      `find`, `find_last`, `for_each`, `some`, `every`, `join`, `reverse`,
      `sort`, `sort_by`, `group_by`, `partition`, `min`, `max`, `min_by`,
      `max_by`, `count`, `count_by`, `slice`, `take`, `take_last`,
      `take_while`, `take_until`, `skip`, `skip_last`, `skip_while`,
      `skip_until`, `entries`/`keys`/`values`, `to_list`/`to_set`/`to_dict`.
      Still open: `flatten`/`flat_map` (deferred — nested-shape semantics
      need more design than the rest of the mixin), `to_seq`, `to_js`.
- [x] Implement `is_(a, b)`: identity fast path, NaN handling, falls back to
      `==` (which each collection overrides via `equals`/`__eq__`).
- [x] Implement `hash_(value)` plus `__hash__`/`__eq__` on every collection
      (shape- and content-based, order-sensitive for `Indexed`, order
      -insensitive for `Keyed`/`SetCollection`), so collections nest as
      `Map`/`Set` keys/values.
- [x] Sentinel convention: `singleton` (in `equality.py`) used project-wide
      as the "not-set-value" default across `get`/`find`/etc.

## Phase 2 — Finish `List`

Close out the type that's already started before moving on.

- [x] Rebuild `List` on top of the Phase 1 base classes/mixin instead of
      ad hoc methods (`immutable/list.py`).
- [x] `set_size`, `equals`/`__eq__`, `__hash__`, `slice` (inherited from the
      mixin). Still open: `with_mutations`/`as_mutable`/`as_immutable`,
      `wasAltered` — deferred to Phase 9, since they only pay off once
      there's a real trie to batch against.
- [x] Fixed correctness gaps: `pop()` no longer takes unused `*values`;
      `set()` now auto-expands (fills with `None`) past the current end,
      matching Immutable.js; `delete()` on an out-of-range index is a no-op
      instead of raising; `map()` now takes a per-element callback instead
      of a whole-list transform; `concat()` no longer silently drops falsy
      scalar arguments (`0`, `False`, `""`) due to a stray truthiness check.
- [x] Expanded `tests/test_immutable.py` plus `tests/test_collection_mixin.py`
      for the inherited mixin behavior.

## Phase 3 — `Map` / `OrderedMap`

- [x] `Map`: `get`, `set`, `has`, `delete`/`remove`, `update`, `update_in`,
      `get_in`, `set_in`, `delete_in`, `merge`, `merge_with`, `merge_deep`,
      `map`, `filter`, `flip` (`immutable/map.py`). Still open:
      `merge_deep_with`, `with_mutations`.
- [x] `OrderedMap`: implemented as a thin `Map` subclass — Python's `dict`
      already preserves insertion order, so no separate backing structure
      was needed (documented in the class docstring).
- [x] Key equality uses Python's own `==`/`hash()`, which our collections
      make *structural* by defining `__eq__`/`__hash__` themselves — so
      nested immutable collections already work correctly as `dict`/`set`
      keys without a separate `is`/`hash` indirection layer.

## Phase 4 — `Set` / `OrderedSet`

- [x] `Set`: `add`, `remove`/`delete`, `union`/`merge`, `intersect`,
      `subtract`, `is_subset`, `is_superset` (`immutable/set.py`).
- [x] `OrderedSet`: same rationale as `OrderedMap` — a thin `Set` subclass.

## Phase 5 — `Stack`

- [x] `push`, `pop`, `peek`, `unshift`/`shift` aliases, `clear`
      (`immutable/stack.py`).

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

- [x] Naming decided and applied consistently: `snake_case` throughout
      (matches PEP 8 and what `List` already had), including `is_()` for
      Immutable.js's `is()` (a Python keyword) and `hash_()` for `hash()`
      (shadows the builtin otherwise). Documented in the README.
- [x] `__repr__` implemented per type (`List([...])`, `Map({...})`,
      `Set([...])`, `Stack([...])`). `__str__` not separately implemented
      (falls back to `__repr__`, which is fine for now).
- [ ] Module-level `fromJS()`/`from_js()` / `toJS()`/`to_js()` for
      recursive conversion to/from plain `dict`/`list` — not yet
      implemented (depends on nothing else being blocked on it, just
      hasn't been done).

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

Phases 1–5 (core abstractions, `List`, `Map`/`OrderedMap`, `Set`/`OrderedSet`,
`Stack`) are done. Next up, in roughly descending priority: Phase 0 (infra —
worth doing now, before the surface area grows further and makes retrofitting
CI/type-checking more painful), Phase 6 (`Record`), then Phase 8's remaining
`fromJS`/`toJS` item. `Seq`/`Range`/`Repeat` (Phase 7) and the trie rewrite
(Phase 9) remain the two phases most worth deferring: both are substantial,
and the current eager/copying implementations are a legitimate v0.1 to ship
and get feedback on first.
