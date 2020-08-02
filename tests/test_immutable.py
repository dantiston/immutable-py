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

    def test_delete(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(a.get(2), 3)
        self.assertEqual(len(a), 3)
        b = a.delete(2)
        self.assertEqual(a.get(2), 3)
        self.assertEqual(len(a), 3)
        self.assertEqual(len(b), 2)
