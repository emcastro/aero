# Placeholder for CPython type annotations

import sys

if sys.implementation.name == "micropython":  # type: ignore
    # pylint: disable=invalid-name
    List = None
    Tuple = None
    Callable = None

    def TypeVar(name):  # pylint: disable=unused-argument
        return None

else:
    from typing import *  # type: ignore
