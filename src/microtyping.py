# Placeholder for CPython type annotations
# pylint: disable=unused-import

import sys

try:
    from typing import TypeVar  # type: ignore
    from typing import Callable, Dict, Generic, List, Tuple

except ImportError:
    if sys.implementation.name == "micropython":  # type: ignore
        # pylint: disable=invalid-name
        List = None
        Tuple = None
        Callable = None
        Dict = None

        class _SpecialForm:
            def __getitem__(self, parameters):
                return object

        Generic = _SpecialForm()

        def TypeVar(name):  # pylint: disable=unused-argument
            return name
