# Placeholder for CPython type annotations

import sys

if sys.implementation.name == "micropython":
    List = None
    Tuple = None
    Callable = None

    def TypeVar(name):
        return None

else:
    from typing import * # type: ignore
