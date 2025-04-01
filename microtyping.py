# Placeholder for CPython type annotations

import sys

if sys.implementation.name == "micropython":
    List = None
else:
    from typing import *
