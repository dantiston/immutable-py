#!/usr/bin/env python3

"""Runs API.md's examples as part of the normal test suite.

`load_tests` is unittest's hook for a test module to contribute tests
that aren't ordinary `TestCase` methods: when discovery imports this
module, it calls `load_tests(loader, tests, pattern)` if present and uses
whatever it returns instead of `tests`. That's what wires API.md's
doctest examples into `python -m unittest discover -s tests`.
"""

import doctest
import os
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_API_DOC = os.path.join(_ROOT, "API.md")


def load_tests(
    loader: unittest.TestLoader, tests: unittest.TestSuite, pattern: str
) -> unittest.TestSuite:
    tests.addTests(
        doctest.DocFileSuite(
            _API_DOC,
            module_relative=False,
            optionflags=doctest.ELLIPSIS,
        )
    )
    return tests


if __name__ == "__main__":
    unittest.main()
