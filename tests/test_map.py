#!/usr/bin/env python3

import unittest

import immutable


class TestMap(unittest.TestCase):
    def test_init_empty(self):
        a = immutable.Map()
        self.assertEqual(len(a), 0)

    def test_init_from_dict(self):
        a = immutable.Map({"a": 1, "b": 2})
        self.assertEqual(a.get("a"), 1)
        self.assertEqual(a.get("b"), 2)

    def test_init_from_pairs(self):
        a = immutable.Map([("a", 1), ("b", 2)])
        self.assertEqual(a.get("a"), 1)

    def test_is_map(self):
        self.assertTrue(immutable.Map.is_map(immutable.Map()))
        self.assertFalse(immutable.Map.is_map({}))

    def test_get_missing_raises(self):
        a = immutable.Map()
        with self.assertRaises(KeyError):
            a.get("missing")

    def test_get_nsv(self):
        a = immutable.Map()
        self.assertEqual(a.get("missing", "default"), "default")

    def test_has(self):
        a = immutable.Map({"a": 1})
        self.assertTrue(a.has("a"))
        self.assertFalse(a.has("b"))
        self.assertTrue("a" in a)

    def test_set_is_immutable(self):
        a = immutable.Map({"a": 1})
        b = a.set("b", 2)
        self.assertFalse(a.has("b"))
        self.assertEqual(b.get("b"), 2)

    def test_delete(self):
        a = immutable.Map({"a": 1, "b": 2})
        b = a.delete("a")
        self.assertTrue(a.has("a"))
        self.assertFalse(b.has("a"))

    def test_delete_missing_is_noop(self):
        a = immutable.Map({"a": 1})
        b = a.delete("missing")
        self.assertTrue(a is b)

    def test_update(self):
        a = immutable.Map({"a": 1})
        b = a.update("a", lambda x: x + 1)
        self.assertEqual(a.get("a"), 1)
        self.assertEqual(b.get("a"), 2)

    def test_update_missing_uses_nsv(self):
        a = immutable.Map()
        b = a.update("a", lambda x: (x or 0) + 1)
        self.assertEqual(b.get("a"), 1)

    def test_flip(self):
        a = immutable.Map({"a": 1, "b": 2})
        b = a.flip()
        self.assertEqual(b.get(1), "a")
        self.assertEqual(b.get(2), "b")

    def test_merge(self):
        a = immutable.Map({"a": 1, "b": 2})
        b = immutable.Map({"b": 3, "c": 4})
        c = a.merge(b)
        self.assertEqual(c.to_dict(), {"a": 1, "b": 3, "c": 4})

    def test_merge_with_dict(self):
        a = immutable.Map({"a": 1})
        c = a.merge({"b": 2})
        self.assertEqual(c.to_dict(), {"a": 1, "b": 2})

    def test_merge_with_function(self):
        a = immutable.Map({"a": 1})
        b = immutable.Map({"a": 2})
        c = a.merge_with(lambda old, new: old + new, b)
        self.assertEqual(c.get("a"), 3)

    def test_merge_deep(self):
        a = immutable.Map({"a": immutable.Map({"x": 1})})
        b = immutable.Map({"a": immutable.Map({"y": 2})})
        c = a.merge_deep(b)
        self.assertEqual(c.get("a").to_dict(), {"x": 1, "y": 2})

    def test_get_in(self):
        a = immutable.Map({"a": immutable.Map({"b": immutable.List((1, 2, 3))})})
        self.assertEqual(a.get_in(["a", "b", 1]), 2)

    def test_get_in_missing_nsv(self):
        a = immutable.Map()
        self.assertEqual(a.get_in(["a", "b"], "default"), "default")

    def test_set_in_creates_path(self):
        a = immutable.Map()
        b = a.set_in(["a", "b"], 1)
        self.assertEqual(b.get_in(["a", "b"]), 1)
        self.assertEqual(a.to_dict(), {})

    def test_update_in(self):
        a = immutable.Map({"a": immutable.Map({"count": 1})})
        b = a.update_in(["a", "count"], lambda x: x + 1)
        self.assertEqual(b.get_in(["a", "count"]), 2)
        self.assertEqual(a.get_in(["a", "count"]), 1)

    def test_delete_in(self):
        a = immutable.Map({"a": immutable.Map({"b": 1, "c": 2})})
        b = a.delete_in(["a", "b"])
        self.assertEqual(b.get_in(["a", "b"], "gone"), "gone")
        self.assertEqual(b.get_in(["a", "c"]), 2)

    def test_map(self):
        a = immutable.Map({"a": 1, "b": 2})
        b = a.map(lambda v: v * 10)
        self.assertEqual(b.to_dict(), {"a": 10, "b": 20})

    def test_filter(self):
        a = immutable.Map({"a": 1, "b": 2, "c": 3})
        b = a.filter(lambda v: v > 1)
        self.assertEqual(b.to_dict(), {"b": 2, "c": 3})

    def test_equals_ignores_insertion_order(self):
        a = immutable.Map({"a": 1, "b": 2})
        b = immutable.Map({"b": 2, "a": 1})
        self.assertEqual(a, b)

    def test_iter_yields_keys(self):
        a = immutable.Map({"a": 1, "b": 2})
        self.assertEqual(set(a), {"a", "b"})

    def test_ordered_map_is_map(self):
        a = immutable.OrderedMap({"a": 1})
        self.assertTrue(immutable.Map.is_map(a))
        self.assertTrue(immutable.OrderedMap.is_ordered_map(a))

    def test_ordered_map_preserves_insertion_order(self):
        keys = [f"k{i}" for i in range(50)]
        a = immutable.OrderedMap((k, i) for i, k in enumerate(keys))
        self.assertEqual(list(a.keys()), keys)

    def test_ordered_map_set_does_not_reorder_existing_key(self):
        a = immutable.OrderedMap([("a", 1), ("b", 2), ("c", 3)])
        b = a.set("a", 100)
        self.assertEqual(list(b.keys()), ["a", "b", "c"])
        self.assertEqual(b.get("a"), 100)

    def test_ordered_map_delete_preserves_remaining_order(self):
        a = immutable.OrderedMap([("a", 1), ("b", 2), ("c", 3)])
        b = a.delete("b")
        self.assertEqual(list(b.keys()), ["a", "c"])

    def test_persistence_across_many_sets(self):
        a = immutable.Map()
        snapshots = []
        for i in range(50):
            a = a.set(i, i * i)
            snapshots.append(a)
        for i, snap in enumerate(snapshots):
            self.assertEqual(len(snap), i + 1)
            self.assertEqual(snap.get(i), i * i)
            if i + 1 < len(snapshots):
                self.assertEqual(snap.get(i + 1, "missing"), "missing")


if __name__ == "__main__":
    unittest.main()
