# Placeholder for MicroPython in CPython

import sys

if sys.implementation.name == "micropython":
    import micropython # type: ignore

else:
    from typing import *

    class micropython:

        @staticmethod
        def native(func):
            return func

    def const(value):
        return value


__all__ = ["micropython", "const"]
