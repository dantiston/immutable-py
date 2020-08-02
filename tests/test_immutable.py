#!/usr/bin/env python3

import unittest

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

    def test_shift_one(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.shift(0)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1, 2, 3, 0])

    def test_shift_many(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.shift(0, 1, 2)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1, 2, 3, 0, 1, 2])

    def test_update(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.update(1, lambda x: x * 4)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1, 8, 3])

    def test_update_all(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a), [1, 2, 3])
        b = a.update_all(lambda values: map(lambda x: x * 2, values))
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [2, 4, 6])

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
