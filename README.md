# quick-codeclimate-adapter

A single monotonic clock function returning a float whose epoch is fixed at construction time, hiding the difference between `time.monotonic` and `time.perf_counter`.

## Usage

```python
from quick_codeclimate_adapter import MonotonicClock, default_clock, monotonic_now

# Use the shared instance directly:
elapsed = default_clock.now()

# Or the convenience function:
elapsed = monotonic_now()

# Or construct your own with a specific backend (e.g. perf_counter for resolution):
clock = MonotonicClock(backend=__import__("time").perf_counter)
t = clock.now()  # relative to clock construction; unit is perf_counter's
```

## Why this exists

`time.monotonic` documents its unit as seconds but not its epoch; `time.perf_counter` documents neither unit nor epoch and varies by platform. Callers who just want "a monotonic float relative to a known moment" must pick one, accept its epoch semantics, and manually subtract a baseline. This adapter does that subtraction once at construction and exposes a single `now()` returning a non-negative float relative to the adapter's own birth.

The trade-off: the adapter performs **no unit conversion**. If you inject `perf_counter` as the backend, the returned floats are in whatever unit `perf_counter` uses on your platform (seconds on most, but not guaranteed). The default backend is `time.monotonic` specifically because its unit *is* documented as seconds. Inject a different backend only if you understand its unit.

## The awkward edge

The very first `now()` call can return `0.0` if the underlying clock has not advanced between construction and the call. This is correct behaviour on high-resolution clocks where no time has elapsed — not a bug. If you need a strictly positive first reading, add your own lower bound in the caller; this library deliberately returns the true elapsed value.

## Running the tests

```
PYTHONPATH=src python -m unittest discover -s tests
```

Zero third-party dependencies. Standard library only.
