#!/usr/bin/env python3

"""Value-equality helpers mirroring Immutable.js's `is` and `hash`."""

# Sentinel distinguishing "no value was passed" from a legitimate `None`,
# used throughout the package as the default for "not-set-value" (nsv)
# parameters (Immutable.js's `notSetValue`).
singleton = object()


def is_(a, b) -> bool:
    """Immutable equality: identity, then NaN-equals-NaN, then `==`."""
    if a is b:
        return True
    if isinstance(a, float) and isinstance(b, float) and a != a and b != b:
        return True
    return a == b


def hash_(value) -> int:
    return hash(value)
