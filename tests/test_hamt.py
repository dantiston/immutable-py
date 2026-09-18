#!/usr/bin/env python3

import random
import unittest

from immutable.equality import singleton
from immutable.hamt import EMPTY, HAMT


class _CollidingKey:
    """Two distinct keys that always hash the same, to force real collisions."""

    def __init__(self, tag):
        self.tag = tag

    def __hash__(self):
        return 42

    def __eq__(self, other):
        return isinstance(other, _CollidingKey) and self.tag == other.tag

    def __repr__(self):
        return f"_CollidingKey({self.tag!r})"


class TestHAMT(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(len(EMPTY), 0)
        self.assertEqual(EMPTY.get("missing", "default"), "default")
        self.assertEqual(list(EMPTY), [])

    def test_set_get(self):
        h = EMPTY.set("a", 1)
        self.assertEqual(h.get("a"), 1)
        self.assertEqual(len(h), 1)

    def test_set_overwrite_does_not_grow(self):
        h = EMPTY.set("a", 1).set("a", 2)
        self.assertEqual(h.get("a"), 2)
        self.assertEqual(len(h), 1)

    def test_set_same_value_returns_same_object(self):
        h = EMPTY.set("a", 1)
        h2 = h.set("a", 1)
        self.assertTrue(h is h2)

    def test_delete(self):
        h = EMPTY.set("a", 1).set("b", 2)
        h2 = h.delete("a")
        self.assertEqual(h2.get("a", singleton), singleton)
        self.assertEqual(h2.get("b"), 2)
        self.assertEqual(len(h2), 1)

    def test_delete_missing_returns_same_object(self):
        h = EMPTY.set("a", 1)
        h2 = h.delete("missing")
        self.assertTrue(h is h2)

    def test_delete_to_empty(self):
        h = EMPTY.set("a", 1).delete("a")
        self.assertEqual(len(h), 0)
        self.assertEqual(list(h), [])

    def test_persistence_across_set(self):
        h1 = EMPTY.set("a", 1)
        h2 = h1.set("a", 2)
        h3 = h1.set("b", 3)
        self.assertEqual(h1.get("a"), 1)
        self.assertEqual(h1.get("b", singleton), singleton)
        self.assertEqual(h2.get("a"), 2)
        self.assertEqual(h3.get("a"), 1)
        self.assertEqual(h3.get("b"), 3)

    def test_persistence_across_delete(self):
        h1 = EMPTY.set("a", 1).set("b", 2)
        h2 = h1.delete("a")
        self.assertEqual(h1.get("a"), 1)
        self.assertEqual(h2.get("a", singleton), singleton)

    def test_many_keys_round_trip(self):
        h = EMPTY
        reference = {}
        for i in range(500):
            h = h.set(i, i * i)
            reference[i] = i * i
        self.assertEqual(len(h), len(reference))
        for k, v in reference.items():
            self.assertEqual(h.get(k), v)
        self.assertEqual(dict(h), reference)

    def test_many_random_string_keys(self):
        rng = random.Random(0)
        keys = [f"key-{i}-{rng.random()}" for i in range(300)]
        h = EMPTY
        reference = {}
        for k in keys:
            v = rng.randint(0, 1000)
            h = h.set(k, v)
            reference[k] = v
        self.assertEqual(dict(h), reference)
        self.assertEqual(len(h), len(reference))

    def test_interleaved_set_delete_matches_dict(self):
        rng = random.Random(1)
        h = EMPTY
        reference = {}
        for _ in range(2000):
            key = rng.randint(0, 50)
            if rng.random() < 0.3 and reference:
                del_key = rng.choice(list(reference))
                h = h.delete(del_key)
                del reference[del_key]
            else:
                value = rng.randint(0, 1000)
                h = h.set(key, value)
                reference[key] = value
        self.assertEqual(dict(h), reference)
        self.assertEqual(len(h), len(reference))

    def test_hash_collision_both_retrievable(self):
        a, b = _CollidingKey("a"), _CollidingKey("b")
        h = EMPTY.set(a, 1).set(b, 2)
        self.assertEqual(h.get(a), 1)
        self.assertEqual(h.get(b), 2)
        self.assertEqual(len(h), 2)

    def test_hash_collision_overwrite(self):
        a, b = _CollidingKey("a"), _CollidingKey("b")
        h = EMPTY.set(a, 1).set(b, 2).set(a, 10)
        self.assertEqual(h.get(a), 10)
        self.assertEqual(h.get(b), 2)
        self.assertEqual(len(h), 2)

    def test_hash_collision_delete_one_keeps_other(self):
        a, b = _CollidingKey("a"), _CollidingKey("b")
        h = EMPTY.set(a, 1).set(b, 2).delete(a)
        self.assertEqual(h.get(a, singleton), singleton)
        self.assertEqual(h.get(b), 2)
        self.assertEqual(len(h), 1)

    def test_iteration_visits_each_entry_once(self):
        h = EMPTY
        for i in range(200):
            h = h.set(i, i)
        seen = [k for k, _ in h]
        self.assertEqual(sorted(seen), list(range(200)))

    def test_bitmap_fanout_beyond_32_children(self):
        # Forces at least one bitmap node past a full 32-way fan-out.
        h = EMPTY
        for i in range(100):
            h = h.set(i, -i)
        for i in range(100):
            self.assertEqual(h.get(i), -i)


if __name__ == "__main__":
    unittest.main()
