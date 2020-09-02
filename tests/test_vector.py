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

    def test_set_present(self):
        a = vector._empty_vector.add(1)
        self.assertEqual(a.set(0, 5).get(0), 5)

    def test_set_empty_end(self):
        a = vector._empty_vector
        self.assertEqual(a.set(0, 5).get(0), 5)

    def test_set_non_empty_end(self):
        a = vector._empty_vector.add(1)
        self.assertEqual(a.get(0), 1)
        self.assertEqual(a.set(1, 5).get(0), 1)
        self.assertEqual(a.set(1, 5).get(1), 5)

    def test_init_set_missing(self):
        with self.assertRaises(Exception):
            vector._empty_vector.set(1, 0)

    def test_add(self):
        a = vector._empty_vector.add(1)
        self.assertEqual(a.get(0), 1)
        self.assertEqual(a.add(2).get(1), 2)

    def test_remove(self):
        a = vector._empty_vector.add(1)
        self.assertEqual(a.get(0), 1)
        self.assertEqual(a.add(2).get(1), 2)

    def test_shift(self):
        a = vector._empty_vector.add(1)
        self.assertEqual(a.get(0), 1)
        self.assertEqual(a.add(2).get(1), 2)

    def test_splice_basic(self):
        a = vector._empty_vector.add(1).add(2).add(3)
        self.assertEqual(list(a), [1, 2, 3])
        b = a.splice(1, 1)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1, 3])

    def test_splice_start(self):
        a = vector._empty_vector.add(1).add(2).add(3)
        self.assertEqual(list(a), [1, 2, 3])
        b = a.splice(0, 1)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [2, 3])

    def test_splice_end(self):
        a = vector._empty_vector.add(1).add(2).add(3)
        self.assertEqual(list(a), [1, 2, 3])
        b = a.splice(2, 1)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1, 2])

    def test_splice_long(self):
        a = vector._empty_vector.add(1).add(2).add(3)
        self.assertEqual(list(a), [1, 2, 3])
        b = a.splice(1, 2)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1])

    def test_splice_over(self):
        a = vector._empty_vector.add(1).add(2).add(3)
        self.assertEqual(list(a), [1, 2, 3])
        b = a.splice(1, 3)
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [1])

    def test_concat_empty(self):
        a = vector._empty_vector.concat([])
        self.assertEqual(len(a), 0)

    def test_concat_one(self):
        a = vector._empty_vector.add(1)
        self.assertEqual(a.get(0), 1)
        self.assertEqual(a.add(2).get(1), 2)

    def test_concat_many(self):
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

    def test_len_empty(self):
        a = vector._empty_vector
        actual = len(a)
        expected = 0
        self.assertEqual(actual, expected)

    def test_len_non_empty(self):
        a = vector._empty_vector.add(1).add(2)
        actual = len(a)
        expected = 2
        self.assertEqual(actual, expected)

    def test_bool_negative(self):
        a = vector._empty_vector
        actual = bool(a)
        self.assertFalse(actual)

    def test_bool_positive(self):
        a = vector._empty_vector.add(1)
        actual = bool(a)
        self.assertTrue(actual)

    def test_iter(self):
        a = vector._empty_vector.add(1).add(2)
        actual = list(a)
        expected = [1, 2]
        self.assertEqual(actual, expected)

    def test_hash_empty(self):
        a = vector._empty_vector
        actual = hash(a)
        expected = 1
        self.assertEqual(actual, expected)

    def test_hash_integer(self):
        a = vector._empty_vector.add(1).add(2)
        actual = hash(a)
        expected = 31 * (31 + hash(1)) + hash(2)
        self.assertEqual(actual, expected)

    def test_hash_strings(self):
        a = vector._empty_vector.add("abc")
        actual = hash(a)
        expected = 31 + hash("abc")
        self.assertEqual(actual, expected)

    def test_eq_negative_different_length(self):
        a = vector._empty_vector.add(1).add(2)
        b = vector._empty_vector.add(1)
        self.assertNotEqual(len(a), len(b))
        self.assertFalse(a == b)

    def test_eq_negative_different_hashes(self):
        a = vector._empty_vector.add(1).add(2)
        b = vector._empty_vector.add(1).add(3)
        self.assertNotEqual(hash(a), hash(b))
        self.assertFalse(a == b)

    def test_eq_negative_different_values(self):
        class BrokenClass(object):
            def __hash__(self):
                return 0

            def __eq__(self, other):
                return self is other

        a = vector._empty_vector.add(BrokenClass())
        b = vector._empty_vector.add(BrokenClass())
        self.assertEqual(hash(a), hash(b))
        self.assertFalse(a == b)

    def test_eq_negative_different_type(self):
        a = vector._empty_vector.add(1).add(2)
        b = "abc"
        self.assertFalse(a == b)

    def test_eq_positive_self(self):
        a = vector._empty_vector.add(1).add(2)
        self.assertTrue(a == a)

    def test_eq_positive_equivalent(self):
        a = vector._empty_vector.add(1).add(2)
        b = vector._empty_vector.add(1).add(2)
        self.assertTrue(a == b)

    def test_eq_positive_reciprocal(self):
        a = vector._empty_vector.add(1).add(2)
        b = vector._empty_vector.add(1).add(2)
        self.assertTrue(a == b)
        self.assertTrue(b == a)

    def test_eq_positive_transitive(self):
        a = vector._empty_vector.add(1).add(2)
        b = vector._empty_vector.add(1).add(2)
        c = vector._empty_vector.add(1).add(2)
        self.assertTrue(a == b)
        self.assertTrue(b == c)
        self.assertTrue(c == a)
