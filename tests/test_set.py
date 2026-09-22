#!/usr/bin/env python3

import unittest

import immutable


class TestSet(unittest.TestCase):
    def test_init_empty(self):
        a = immutable.Set()
        self.assertEqual(len(a), 0)

    def test_init_dedupes(self):
        a = immutable.Set([1, 2, 2, 3, 1])
        self.assertEqual(len(a), 3)

    def test_of(self):
        a = immutable.Set.of(1, 2, 3)
        self.assertEqual(set(a), {1, 2, 3})

    def test_is_set(self):
        self.assertTrue(immutable.Set.is_set(immutable.Set()))
        self.assertFalse(immutable.Set.is_set({1, 2, 3}))

    def test_has(self):
        a = immutable.Set([1, 2, 3])
        self.assertTrue(a.has(1))
        self.assertFalse(a.has(4))
        self.assertTrue(1 in a)

    def test_add(self):
        a = immutable.Set([1, 2])
        b = a.add(3)
        self.assertEqual(set(a), {1, 2})
        self.assertEqual(set(b), {1, 2, 3})

    def test_add_existing_is_noop(self):
        a = immutable.Set([1, 2])
        b = a.add(1)
        self.assertTrue(a is b)

    def test_delete(self):
        a = immutable.Set([1, 2, 3])
        b = a.delete(2)
        self.assertEqual(set(a), {1, 2, 3})
        self.assertEqual(set(b), {1, 3})

    def test_delete_missing_is_noop(self):
        a = immutable.Set([1, 2])
        b = a.delete(99)
        self.assertTrue(a is b)

    def test_union(self):
        a = immutable.Set([1, 2])
        b = immutable.Set([2, 3])
        self.assertEqual(set(a.union(b)), {1, 2, 3})

    def test_intersect(self):
        a = immutable.Set([1, 2, 3])
        b = immutable.Set([2, 3, 4])
        self.assertEqual(set(a.intersect(b)), {2, 3})

    def test_subtract(self):
        a = immutable.Set([1, 2, 3])
        b = immutable.Set([2])
        self.assertEqual(set(a.subtract(b)), {1, 3})

    def test_is_subset(self):
        a = immutable.Set([1, 2])
        b = immutable.Set([1, 2, 3])
        self.assertTrue(a.is_subset(b))
        self.assertFalse(b.is_subset(a))

    def test_is_superset(self):
        a = immutable.Set([1, 2, 3])
        b = immutable.Set([1, 2])
        self.assertTrue(a.is_superset(b))
        self.assertFalse(b.is_superset(a))

    def test_map_dedupes(self):
        a = immutable.Set([1, 2, 3])
        b = a.map(lambda v: v % 2)
        self.assertEqual(set(b), {0, 1})

    def test_equals_ignores_order(self):
        a = immutable.Set([1, 2, 3])
        b = immutable.Set([3, 2, 1])
        self.assertEqual(a, b)

    def test_ordered_set_is_set(self):
        a = immutable.OrderedSet([1, 2])
        self.assertTrue(immutable.Set.is_set(a))
        self.assertTrue(immutable.OrderedSet.is_ordered_set(a))

    def test_ordered_set_preserves_insertion_order(self):
        values = [f"v{i}" for i in range(50)]
        a = immutable.OrderedSet(values)
        self.assertEqual(list(a), values)

    def test_ordered_set_re_add_does_not_reorder(self):
        a = immutable.OrderedSet(["a", "b", "c"])
        b = a.add("a")
        self.assertTrue(a is b)
        self.assertEqual(list(b), ["a", "b", "c"])

    def test_ordered_set_delete_preserves_remaining_order(self):
        a = immutable.OrderedSet(["a", "b", "c"])
        b = a.delete("b")
        self.assertEqual(list(b), ["a", "c"])

    def test_of_is_polymorphic(self):
        a = immutable.OrderedSet.of(1, 2, 3)
        self.assertIsInstance(a, immutable.OrderedSet)
        self.assertEqual(list(a), [1, 2, 3])

    def test_persistence_across_many_adds(self):
        a = immutable.Set()
        snapshots = []
        for i in range(50):
            a = a.add(i)
            snapshots.append(a)
        for i, snap in enumerate(snapshots):
            self.assertEqual(len(snap), i + 1)
            self.assertTrue(snap.has(i))
            if i + 1 < len(snapshots):
                self.assertFalse(snap.has(i + 1))

    def test_set_wraps_a_map(self):
        a = immutable.Set([1, 2, 3])
        self.assertIsInstance(a._map, immutable.Map)
        self.assertNotIsInstance(a._map, immutable.OrderedMap)

    def test_ordered_set_wraps_an_ordered_map(self):
        a = immutable.OrderedSet([1, 2, 3])
        self.assertIsInstance(a._map, immutable.OrderedMap)

    def test_ordered_set_reuses_set_methods(self):
        # OrderedSet defines no add/delete/has/__iter__/__len__ of its
        # own - it only overrides which Map subtype backs it. Confirm
        # that's still true rather than silently regressing to a copy.
        for name in ("add", "delete", "has", "__iter__", "__len__", "union"):
            self.assertIs(
                getattr(immutable.OrderedSet, name),
                getattr(immutable.Set, name),
            )


if __name__ == "__main__":
    unittest.main()
