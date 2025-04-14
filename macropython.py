# Placeholder for MicroPython in CPython

import sys

if sys.implementation.name == "micropython":
    import micropython

else:
    from typing import *

    class micropython:

        @staticmethod
        def native(func):
            return func


__all__ = ["micropython"]
