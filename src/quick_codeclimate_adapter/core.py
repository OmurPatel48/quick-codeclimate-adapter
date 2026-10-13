# SPDX-License-Identifier: MIT
"""Core clock implementation.

Design rationale
----------------
There are two candidate monotonic primitives in the standard library:
  * time.monotonic()   — returns seconds as a float. Not guaranteed to be
                         high-resolution, but its epoch is unspecified and
                         may differ between Python interpreter runs.
  * time.perf_counter()— returns a float whose unit is *not defined*; on some
                         platforms it is seconds, on others it is not.
                         However, it is the highest-resolution monotonic clock.

This adapter picks time.monotonic by default because the unit is documented
as seconds. A caller who needs finer resolution may inject perf_counter as
the backend; the adapter subtracts a captured baseline so the reported value
is relative to the adapter's own construction moment (the "stable epoch"),
rather than to whatever arbitrary epoch the underlying clock happens to use.

The subtraction is done in the backend's own unit space, so no unit
conversion is attempted. The returned float is simply backend_now minus
backend_at_construction. This means: if you inject perf_counter and its unit
is microseconds, every value returned will be in microseconds. The caller is
responsible for knowing which backend they injected.
"""

from __future__ import annotations

import time
from typing import Callable, Optional


class MonotonicClock:
    """A monotonic clock whose epoch is fixed at construction time.

    Parameters
    ----------
    backend:
        A callable returning a float that never decreases during a single
        interpreter process. Defaults to time.monotonic. Passing
        time.perf_counter is supported; note that perf_counter's unit is
        implementation-defined, so values will be in whatever unit the backend
        uses.
    """

    __slots__ = ("_backend", "_origin", "__weakref__")

    def __init__(self, backend: Optional[Callable[[], float]] = None) -> None:
        if backend is None:
            backend = time.monotonic
        # Capture the baseline *before* anything else can call us so that the
        # stable epoch is as close as possible to construction. We read the
        # backend once and store the raw value; later reads subtract it.
        # Reading it here (rather than lazily on first now()) guarantees that
        # the epoch is deterministic with respect to construction time, not
        # to first use — which is the property the brief calls "stable epoch".
        self._backend: Callable[[], float] = backend
        self._origin: float = backend()

    def now(self) -> float:
        """Return elapsed time since construction, in the backend's unit.

        The value is guaranteed non-negative *between successive calls*
        because the underlying clock is monotonic, but the very first call
        could in principle return 0.0 if the backend did not advance between
        construction and the call. That is an acceptable edge: it reflects
        real elapsed time of zero on high-resolution clocks.
        """
        return self._backend() - self._origin

    def __call__(self) -> float:
        """Allow ``clock()`` as shorthand for ``clock.now()``."""
        return self.now()


# A single shared instance so callers who do not need per-component epochs can
# import one name and go. Its epoch is fixed at module import time.
default_clock: MonotonicClock = MonotonicClock()


def monotonic_now() -> float:
    """Return the current reading of ``default_clock``.

    This exists so callers can write ``from quick_codeclimate_adapter import
    monotonic_now`` without holding a reference to the clock instance.
    """
    return default_clock.now()
