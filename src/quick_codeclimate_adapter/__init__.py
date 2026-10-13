# SPDX-License-Identifier: MIT
"""quick-codeclimate-adapter — a single monotonic clock with a stable epoch.

Public surface:
    MonotonicClock   — class wrapping a backend monotonic function.
    default_clock    — module-level instance ready for immediate use.
    monotonic_now    — convenience function delegating to default_clock.

The adapter hides the minute differences between time.monotonic and
perf_counter (different units, different epoch semantics) behind one
float-returning callable whose epoch is fixed at construction time.
"""

from quick_codeclimate_adapter.core import (
    MonotonicClock,
    default_clock,
    monotonic_now,
)

__all__ = [
    "MonotonicClock",
    "default_clock",
    "monotonic_now",
]
