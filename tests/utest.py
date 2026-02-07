import builtins

# Import module patches
from macropython.micropython import *  # type: ignore


# Add micropython new builtins
def const(value):
    return value


builtins.const = const  # type: ignore
