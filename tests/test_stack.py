#!/usr/bin/env python3

import unittest

import immutable


class TestStack(unittest.TestCase):
    def test_init_empty(self):
        a = immutable.Stack()
        self.assertEqual(len(a), 0)

    def test_of(self):
        a = immutable.Stack.of(1, 2, 3)
        self.assertEqual(list(a), [1, 2, 3])

    def test_is_stack(self):
        self.assertTrue(immutable.Stack.is_stack(immutable.Stack()))
        self.assertFalse(immutable.Stack.is_stack([1, 2, 3]))

    def test_peek(self):
        a = immutable.Stack((1, 2, 3))
        self.assertEqual(a.peek(), 1)

    def test_peek_nsv(self):
        a = immutable.Stack()
        self.assertEqual(a.peek(0), 0)

    def test_push_single(self):
        a = immutable.Stack((2, 3))
        b = a.push(1)
        self.assertEqual(list(a), [2, 3])
        self.assertEqual(list(b), [1, 2, 3])

    def test_push_many_puts_last_on_top(self):
        a = immutable.Stack()
        b = a.push(1, 2, 3)
        self.assertEqual(list(b), [3, 2, 1])
        self.assertEqual(b.peek(), 3)

    def test_pop(self):
        a = immutable.Stack((1, 2, 3))
        b = a.pop()
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [2, 3])

    def test_pop_empty_is_noop(self):
        a = immutable.Stack()
        b = a.pop()
        self.assertTrue(a is b)

    def test_clear(self):
        a = immutable.Stack((1, 2, 3))
        b = a.clear()
        self.assertEqual(list(b), [])

    def test_equals(self):
        a = immutable.Stack((1, 2, 3))
        b = immutable.Stack((1, 2, 3))
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
