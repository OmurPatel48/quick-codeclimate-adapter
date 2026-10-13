# SPDX-License-Identifier: MIT
"""Tests for quick_codeclimate_adapter.core.

Determinism rules followed here:
  * No real sleeps — we inject a fake backend.
  * No equality on floats — we use assertAlmostEqual or compare ranges.
  * No wall-clock assertions.
"""

import math
import time
import unittest

from quick_codeclimate_adapter import (
    MonotonicClock,
    default_clock,
    monotonic_now,
)


class _FakeClock:
    """A controllable monotonic source for deterministic tests."""

    def __init__(self, start: float = 0.0) -> None:
        self._t = start
        self.calls = 0

    def __call__(self) -> float:
        self.calls += 1
        return self._t

    def advance(self, delta: float) -> None:
        self._t += delta


class TestMonotonicClock(unittest.TestCase):
    def test_now_returns_float(self) -> None:
        fake = _FakeClock(start=100.0)
        clock = MonotonicClock(backend=fake)
        self.assertIsInstance(clock.now(), float)

    def test_first_call_is_zero(self) -> None:
        # The origin is captured at construction. If the fake clock hasn't
        # advanced, the first reading is exactly 0.0.
        fake = _FakeClock(start=50.0)
        clock = MonotonicClock(backend=fake)
        self.assertEqual(clock.now(), 0.0)

    def test_now_reflects_elapsed_since_construction(self) -> None:
        fake = _FakeClock(start=1000.0)
        clock = MonotonicClock(backend=fake)
        fake.advance(5.0)
        self.assertAlmostEqual(clock.now(), 5.0, places=9)

    def test_epoch_is_stable_across_calls(self) -> None:
        # Two readings taken at different fake times should differ by the
        # exact delta, and both are relative to the *same* origin.
        fake = _FakeClock(start=200.0)
        clock = MonotonicClock(backend=fake)
        fake.advance(3.0)
        first = clock.now()
        fake.advance(4.0)
        second = clock.now()
        self.assertAlmostEqual(second - first, 4.0, places=9)

    def test_default_backend_is_time_monotonic(self) -> None:
        # We don't assert on the value, only that the clock works without a
        # backend argument and returns a non-negative float.
        clock = MonotonicClock()
        value = clock.now()
        self.assertIsInstance(value, float)
        self.assertGreaterEqual(value, 0.0)

    def test_call_is_alias_for_now(self) -> None:
        fake = _FakeClock(start=10.0)
        clock = MonotonicClock(backend=fake)
        fake.advance(2.0)
        self.assertAlmostEqual(clock(), clock.now(), places=12)

    def test_origin_is_captured_at_construction_not_first_call(self) -> None:
        # If the fake advances between construction and the first now() call,
        # the first reading must already reflect that delta — proving the
        # epoch was fixed at construction.
        fake = _FakeClock(start=0.0)
        clock = MonotonicClock(backend=fake)
        fake.advance(7.0)
        self.assertAlmostEqual(clock.now(), 7.0, places=9)

    def test_negative_delta_does_not_occur_for_monotonic_backend(self) -> None:
        # A monotonic backend never goes backwards, so now() must be >= 0.
        # We simulate a non-advancing clock across multiple calls.
        fake = _FakeClock(start=5.0)
        clock = MonotonicClock(backend=fake)
        for _ in range(5):
            self.assertGreaterEqual(clock.now(), 0.0)

    def test_perf_counter_backend_supported(self) -> None:
        # We don't assert on the value (unit is platform-dependent), only that
        # it runs and returns a float. Two successive calls are ordered.
        clock = MonotonicClock(backend=time.perf_counter)
        a = clock.now()
        b = clock.now()
        self.assertIsInstance(a, float)
        self.assertIsInstance(b, float)
        self.assertGreaterEqual(b, a)

    def test_subclass_is_not_required(self) -> None:
        # Ensure the class is usable without subclassing — the public API is
        # concrete.
        clock = MonotonicClock(backend=_FakeClock())
        self.assertIsInstance(clock, MonotonicClock)

    def test_default_clock_and_monotonic_now_are_consistent(self) -> None:
        a = default_clock.now()
        b = monotonic_now()
        # Both read the same underlying default_clock, so b >= a.
        self.assertGreaterEqual(b, a)

    def test_monotonic_now_returns_float(self) -> None:
        self.assertIsInstance(monotonic_now(), float)


if __name__ == "__main__":
    unittest.main()
