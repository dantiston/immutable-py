#!/usr/bin/env python3

import random
import unittest

from immutable.vector import EMPTY, Vector


class TestVector(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(len(EMPTY), 0)
        self.assertEqual(list(EMPTY), [])

    def test_empty_get_raises(self):
        with self.assertRaises(IndexError):
            EMPTY.get(0)

    def test_empty_pop_raises(self):
        with self.assertRaises(IndexError):
            EMPTY.pop()

    def test_push_get(self):
        v = EMPTY.push(1).push(2).push(3)
        self.assertEqual(len(v), 3)
        self.assertEqual(v.get(0), 1)
        self.assertEqual(v.get(1), 2)
        self.assertEqual(v.get(2), 3)
        self.assertEqual(list(v), [1, 2, 3])

    def test_get_out_of_range_raises(self):
        v = EMPTY.push(1)
        with self.assertRaises(IndexError):
            v.get(1)
        with self.assertRaises(IndexError):
            v.get(-1)

    def test_set(self):
        v = EMPTY.push(1).push(2).push(3)
        v2 = v.set(1, "x")
        self.assertEqual(list(v), [1, 2, 3])
        self.assertEqual(list(v2), [1, "x", 3])

    def test_pop(self):
        v = EMPTY.push(1).push(2).push(3)
        v2 = v.pop()
        self.assertEqual(list(v), [1, 2, 3])
        self.assertEqual(list(v2), [1, 2])

    def test_pop_to_single_returns_empty(self):
        v = EMPTY.push(1).pop()
        self.assertEqual(len(v), 0)
        self.assertEqual(list(v), [])

    def test_persistence_across_push(self):
        v1 = EMPTY.push(1)
        v2 = v1.push(2)
        v3 = v1.push(3)
        self.assertEqual(list(v1), [1])
        self.assertEqual(list(v2), [1, 2])
        self.assertEqual(list(v3), [1, 3])

    def test_persistence_across_set(self):
        v1 = EMPTY.push(1).push(2)
        v2 = v1.set(0, "changed")
        self.assertEqual(list(v1), [1, 2])
        self.assertEqual(list(v2), ["changed", 2])

    def test_persistence_across_pop(self):
        v1 = EMPTY.push(1).push(2).push(3)
        v2 = v1.pop()
        self.assertEqual(list(v1), [1, 2, 3])
        self.assertEqual(list(v2), [1, 2])

    def test_crosses_tail_boundary(self):
        v = Vector.from_iterable(range(32))
        self.assertEqual(list(v), list(range(32)))
        v = v.push(32)
        self.assertEqual(list(v), list(range(33)))
        self.assertEqual(v.get(0), 0)
        self.assertEqual(v.get(32), 32)

    def test_crosses_root_overflow_boundary(self):
        v = Vector.from_iterable(range(64))
        self.assertEqual(list(v), list(range(64)))
        for i in range(64):
            self.assertEqual(v.get(i), i)

    def test_large_push_and_get(self):
        n = 32 * 32 * 3 + 17
        v = Vector.from_iterable(range(n))
        self.assertEqual(len(v), n)
        self.assertEqual(v.get(0), 0)
        self.assertEqual(v.get(n - 1), n - 1)
        self.assertEqual(v.get(n // 2), n // 2)
        self.assertEqual(list(v), list(range(n)))

    def test_pop_all_the_way_down(self):
        n = 200
        v = Vector.from_iterable(range(n))
        for expected_len in range(n, 0, -1):
            self.assertEqual(len(v), expected_len)
            v = v.pop()
        self.assertEqual(len(v), 0)

    def test_set_across_trie_and_tail(self):
        n = 100
        v = Vector.from_iterable(range(n))
        v = v.set(0, "first").set(50, "middle").set(99, "last")
        result = list(v)
        self.assertEqual(result[0], "first")
        self.assertEqual(result[50], "middle")
        self.assertEqual(result[99], "last")

    def test_randomized_against_list_oracle(self):
        rng = random.Random(42)
        v = EMPTY
        ref = []
        for _ in range(5000):
            op = rng.random()
            if op < 0.55 or not ref:
                val = rng.randint(0, 1000)
                v = v.push(val)
                ref.append(val)
            elif op < 0.8:
                v = v.pop()
                ref.pop()
            else:
                idx = rng.randrange(len(ref))
                val = rng.randint(0, 1000)
                v = v.set(idx, val)
                ref[idx] = val
        self.assertEqual(len(v), len(ref))
        self.assertEqual(list(v), ref)
        for i, x in enumerate(ref):
            self.assertEqual(v.get(i), x)


if __name__ == "__main__":
    unittest.main()
