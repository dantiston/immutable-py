#!/usr/bin/env python3

import unittest

import immutable


class TestCollectionMixinOnList(unittest.TestCase):
    def test_filter(self):
        a = immutable.List((1, 2, 3, 4))
        b = a.filter(lambda x: x % 2 == 0)
        self.assertEqual(list(b), [2, 4])

    def test_filter_not(self):
        a = immutable.List((1, 2, 3, 4))
        b = a.filter_not(lambda x: x % 2 == 0)
        self.assertEqual(list(b), [1, 3])

    def test_reduce(self):
        a = immutable.List((1, 2, 3, 4))
        self.assertEqual(a.reduce(lambda acc, x: acc + x), 10)
        self.assertEqual(a.reduce(lambda acc, x: acc + x, 100), 110)

    def test_reduce_right(self):
        a = immutable.List(("a", "b", "c"))
        self.assertEqual(a.reduce_right(lambda acc, x: acc + x), "cba")

    def test_find(self):
        a = immutable.List((1, 2, 3, 4))
        self.assertEqual(a.find(lambda x: x > 2), 3)

    def test_find_not_found_raises(self):
        a = immutable.List((1, 2))
        with self.assertRaises(ValueError):
            a.find(lambda x: x > 10)

    def test_find_nsv(self):
        a = immutable.List((1, 2))
        self.assertEqual(a.find(lambda x: x > 10, -1), -1)

    def test_some_and_every(self):
        a = immutable.List((1, 2, 3))
        self.assertTrue(a.some(lambda x: x > 2))
        self.assertFalse(a.every(lambda x: x > 2))
        self.assertTrue(a.every(lambda x: x > 0))

    def test_for_each(self):
        a = immutable.List((1, 2, 3))
        seen = []
        a.for_each(seen.append)
        self.assertEqual(seen, [1, 2, 3])

    def test_count(self):
        a = immutable.List((1, 2, 3, 4))
        self.assertEqual(a.count(), 4)
        self.assertEqual(a.count(lambda x: x % 2 == 0), 2)

    def test_count_by(self):
        a = immutable.List((1, 2, 3, 4, 5))
        self.assertEqual(a.count_by(lambda x: x % 2), {1: 3, 0: 2})

    def test_min_max(self):
        a = immutable.List((3, 1, 4, 1, 5))
        self.assertEqual(a.min(), 1)
        self.assertEqual(a.max(), 5)

    def test_min_by_max_by(self):
        a = immutable.List(("aaa", "b", "cc"))
        self.assertEqual(a.min_by(len), "b")
        self.assertEqual(a.max_by(len), "aaa")

    def test_sort(self):
        a = immutable.List((3, 1, 2))
        self.assertEqual(list(a.sort()), [1, 2, 3])
        self.assertEqual(list(a.sort(reverse=True)), [3, 2, 1])

    def test_sort_by(self):
        a = immutable.List(("aaa", "b", "cc"))
        self.assertEqual(list(a.sort_by(len)), ["b", "cc", "aaa"])

    def test_reverse(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(list(a.reverse()), [3, 2, 1])

    def test_group_by(self):
        a = immutable.List((1, 2, 3, 4, 5))
        groups = a.group_by(lambda x: x % 2)
        self.assertEqual(list(groups[0]), [2, 4])
        self.assertEqual(list(groups[1]), [1, 3, 5])

    def test_partition(self):
        a = immutable.List((1, 2, 3, 4))
        falsy, truthy = a.partition(lambda x: x % 2 == 0)
        self.assertEqual(list(falsy), [1, 3])
        self.assertEqual(list(truthy), [2, 4])

    def test_slice(self):
        a = immutable.List((1, 2, 3, 4, 5))
        self.assertEqual(list(a.slice(1, 3)), [2, 3])

    def test_take_and_skip(self):
        a = immutable.List((1, 2, 3, 4, 5))
        self.assertEqual(list(a.take(2)), [1, 2])
        self.assertEqual(list(a.skip(2)), [3, 4, 5])
        self.assertEqual(list(a.take_last(2)), [4, 5])
        self.assertEqual(list(a.skip_last(2)), [1, 2, 3])

    def test_take_while_and_skip_while(self):
        a = immutable.List((1, 2, 3, 4, 1))
        self.assertEqual(list(a.take_while(lambda x: x < 3)), [1, 2])
        self.assertEqual(list(a.skip_while(lambda x: x < 3)), [3, 4, 1])

    def test_join(self):
        a = immutable.List((1, 2, 3))
        self.assertEqual(a.join(), "1,2,3")
        self.assertEqual(a.join("-"), "1-2-3")

    def test_to_list_to_set(self):
        a = immutable.List((1, 2, 2, 3))
        self.assertEqual(a.to_list(), [1, 2, 2, 3])
        self.assertEqual(a.to_set(), {1, 2, 3})


class TestCollectionMixinOnMap(unittest.TestCase):
    def test_reduce_over_values(self):
        a = immutable.Map({"a": 1, "b": 2, "c": 3})
        self.assertEqual(a.reduce(lambda acc, x: acc + x, 0), 6)

    def test_count_by(self):
        a = immutable.Map({"a": 1, "b": 2, "c": 3, "d": 4})
        self.assertEqual(a.count_by(lambda v: v % 2), {1: 2, 0: 2})


class TestEquality(unittest.TestCase):
    def test_is_identity(self):
        a = immutable.List((1, 2, 3))
        self.assertTrue(immutable.is_(a, a))

    def test_is_nan(self):
        nan = float("nan")
        self.assertTrue(immutable.is_(nan, nan))

    def test_is_value_equality(self):
        a = immutable.List((1, 2, 3))
        b = immutable.List((1, 2, 3))
        self.assertTrue(immutable.is_(a, b))

    def test_hash_matches_builtin(self):
        self.assertEqual(immutable.hash_(1), hash(1))


if __name__ == "__main__":
    unittest.main()
