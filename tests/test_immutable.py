#!/usr/bin/env python3

import unittest

from functools import reduce

import immutable


class TestImmutableList(unittest.TestCase):
    def test_init_empty(self):
        a = immutable.List()
        self.assertEqual(len(a), 0)

    def test_init_get(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(a.get(0), 1)
        self.assertEqual(a.get(1), 2)
        self.assertEqual(a.get(2), 3)

    def test_of_empty(self):
        a = immutable.List.of()
        self.assertEqual(len(a), 0)

    def test_of_get(self):
        a = immutable.List.of(1, 2, 3)
        self.assertEqual(a.get(0), 1)
        self.assertEqual(a.get(1), 2)
        self.assertEqual(a.get(2), 3)

    def test_is_list_negative(self):
        a = [1, 2, 3]
        self.assertFalse(immutable.List.is_list(a))

    def test_is_list_positive(self):
        a = immutable.List.of(1, 2, 3)
        self.assertTrue(immutable.List.is_list(a))

    def test_get_nsv(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(a.get(3, 4), 4)

    def test_includes(self):
        a = immutable.List((1, 2, 3))
        self.assertTrue(a.includes(1))
        self.assertTrue(a.includes(2))
        self.assertTrue(a.includes(3))
        self.assertFalse(a.includes(4))

    def test_contains(self):
        a = immutable.List((1, 2, 3))
        self.assertTrue(1 in a)
        self.assertTrue(2 in a)
        self.assertTrue(3 in a)
        self.assertFalse(4 in a)

    def test_first(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(a.first(), 1)

    def test_first_nsv(self):
        a = immutable.List()
        self.assertEqual(a.first(0), 0)

    def test_last(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(a.last(), 3)

    def test_last_nsv(self):
        a = immutable.List()
        self.assertEqual(a.last(0), 0)

    def test_set(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.set(1, 7)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1, 7, 3])

    def test_delete(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.delete(2)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1, 2])

    def test_insert(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.insert(1, 4)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1, 4, 2, 3])

    def test_clear(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.clear()
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [])

    def test_push_one(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.push(4)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1, 2, 3, 4])

    def test_push_many(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.push(4, 5, 6)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1, 2, 3, 4, 5, 6])

    def test_pop(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.pop()
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1, 2])

    def test_unshift_one(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.unshift(0)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [0, 1, 2, 3])

    def test_unshift_many(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(len(a), 3)
        b = a.unshift(0, 1, 2)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [0, 1, 2, 1, 2, 3])

    def test_shift(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.shift()
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [2, 3])

    def test_update(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.update(1, lambda x: x * 4)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1, 8, 3])

    def test_thru(self):
        def sum(collection):
            return reduce(lambda l, r: l + r, collection)

        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.thru(sum)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(b, 6)

    def test_concat_empty(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.concat()
        self.assertEqual(list(b), [1, 2, 3])
        self.assertTrue(a is b)

    def test_concat_values(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.concat(4, 5, 6)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1, 2, 3, 4, 5, 6])

    def test_concat_collection(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.concat([4, 5, 6])
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1, 2, 3, 4, 5, 6])

    def test_concat_collections(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.concat([4, 5, 6], [7, 8])
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1, 2, 3, 4, 5, 6, 7, 8])

    def test_concat_immutable_collections(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.concat(immutable.List((4, 5, 6)))
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1, 2, 3, 4, 5, 6])

    def test_concat_mixed(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.concat([4, 5, 6], 7, immutable.List((8, 9, 10)))
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_map(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.map(lambda x: x * 2)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [2, 4, 6])

    def test_set_extends_list(self):
        a = immutable.List((1, 2, 3))
        b = a.set(4, "z")
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1, 2, 3, None, "z"])

    def test_delete_out_of_range_is_noop(self):
        a = immutable.List((1, 2, 3))
        b = a.delete(10)
        self.assertTrue(a is b)

    def test_concat_falsy_value(self):
        a = immutable.List((1, 2, 3))
        b = a.concat(0, False, "")
        self.assertEqual(list(b), [1, 2, 3, 0, False, ""])

    def test_equals(self):
        a = immutable.List((1, 2, 3))
        b = immutable.List((1, 2, 3))
        c = immutable.List((1, 2, 4))
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_hash_equal_lists(self):
        a = immutable.List((1, 2, 3))
        b = immutable.List((1, 2, 3))
        self.assertEqual(hash(a), hash(b))

    def test_len(self):
        a = immutable.List((1, 2, 3))
        actual = len(a)
        expected = 3
        self.assertEqual(actual, expected)

    def test_iter(self):
        a = immutable.List((1, 2, 3))
        actual = list(a)
        expected = [1, 2, 3]
        self.assertEqual(actual, expected)

    def test_large_scale_push_persistence(self):
        a = immutable.List()
        snapshots = []
        for i in range(200):
            a = a.push(i)
            snapshots.append(a)
        for i, snap in enumerate(snapshots):
            self.assertEqual(len(snap), i + 1)
            self.assertEqual(list(snap), list(range(i + 1)))
            self.assertEqual(snap.get(0), 0)
            self.assertEqual(snap.get(-1), i)

    def test_large_scale_pop_all_the_way(self):
        a = immutable.List(range(200))
        while len(a) > 0:
            expected_len = len(a) - 1
            a = a.pop()
            self.assertEqual(len(a), expected_len)
            self.assertEqual(list(a), list(range(expected_len)))

    def test_large_scale_set(self):
        a = immutable.List(range(200))
        b = a.set(150, "changed")
        self.assertEqual(a.get(150), 150)
        self.assertEqual(b.get(150), "changed")
        self.assertEqual(len(b), 200)

    def test_negative_get_across_scale(self):
        a = immutable.List(range(100))
        self.assertEqual(a.get(-1), 99)
        self.assertEqual(a.get(-100), 0)
        with self.assertRaises(IndexError):
            a.get(-101)
