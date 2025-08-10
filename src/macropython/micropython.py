import gc
import time

# Emulate the micropython module in a way that is compatible with Python


# Emulate microptyhon decorators
def identity_decorator(func):
    return func


# @micropython.native
native = identity_decorator


## time


def _ticks_ms():
    """Return the number of milliseconds since the system started."""
    return int(time.time() * 1000)


def _tick_diff(t2, t1):
    """Return the difference in milliseconds between two ticks."""
    return t2 - t1


time.ticks_ms = _ticks_ms
time.ticks_diff = _tick_diff

## gc


def _mem_free():
    """Simulate 1MB of free memory"""
    return 1_000_000


gc.mem_free = _mem_free
