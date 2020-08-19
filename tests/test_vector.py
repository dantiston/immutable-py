#!/usr/bin/env python3

import unittest

from immutable import vector


class TestVector(unittest.TestCase):
    def test_init_empty(self):
        a = vector.Vector(0, 5, vector.Node(children=[]), [])
        self.assertEqual(len(a), 0)

    def test_init_get(self):
        a = vector._empty_vector.add(1)
        self.assertEqual(a.get(0), 1)

    def test_get_nsv(self):
        a = vector._empty_vector.add(1)
        self.assertEqual(a.get(1, 2), 2)

    def test_init_set_present(self):
        a = vector._empty_vector.add(1)
        self.assertEqual(a.set(0, 5).get(0), 5)

    def test_init_set_empty_end(self):
        a = vector._empty_vector
        self.assertEqual(a.set(0, 5).get(0), 5)

    def test_init_set_non_empty_end(self):
        a = vector._empty_vector.add(1)
        self.assertEqual(a.get(0), 1)
        self.assertEqual(a.set(1, 5).get(0), 1)
        self.assertEqual(a.set(1, 5).get(1), 5)

    def test_init_set_missing(self):
        with self.assertRaises(Exception):
            vector._empty_vector.set(1, 0)

    def test_init_add(self):
        a = vector._empty_vector.add(1)
        self.assertEqual(a.get(0), 1)
        self.assertEqual(a.add(2).get(1), 2)

    def test_contains_positive(self):
        a = vector._empty_vector.add(1).add(2)
        self.assertTrue(1 in a)
        self.assertTrue(2 in a)

    def test_contains_negative(self):
        a = vector._empty_vector.add(1).add(2)
        self.assertFalse(0 in a)
        self.assertFalse(3 in a)

    def test_len(self):
        a = vector._empty_vector.add(1).add(2)
        actual = len(a)
        expected = 2
        self.assertEqual(actual, expected)

    def test_iter(self):
        a = vector._empty_vector.add(1).add(2)
        actual = list(a)
        expected = [1, 2]
        self.assertEqual(actual, expected)
