# Placeholder for CPython type annotations
# pylint: disable=unused-import

import sys

if sys.implementation.name == "micropython":  # type: ignore
    # pylint: disable=invalid-name
    List = None
    Tuple = None
    Callable = None
    Dict = None

    def TypeVar(name):  # pylint: disable=unused-argument
        return None

else:
    from typing import List, Tuple, Callable, Dict
    from typing import TypeVar  # type: ignore
