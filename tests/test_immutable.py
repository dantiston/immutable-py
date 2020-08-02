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

    def test_flat_map_flat(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.flat_map(lambda x: x * 2)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [2, 4, 6])

    def test_flat_map_nested(self):
        a = immutable.List((immutable.List((1, 1, 1)), immutable.List((2, 2, 2)), immutable.List((3, 3, 3))))
        self.assertEqual([list(x) for x in a], [[1, 1, 1], [2, 2, 2], [3, 3, 3]])
        b = a.flat_map(lambda x: x * 2)
        self.assertEqual([list(x) for x in a], [[1, 1, 1], [2, 2, 2], [3, 3, 3]])
        self.assertEqual(list(b), [2, 2, 2, 4, 4, 4, 6, 6, 6])

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
