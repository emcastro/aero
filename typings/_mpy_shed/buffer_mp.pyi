from array import array

from _typeshed import AnyStr_co, Incomplete, structseq
from typing_extensions import TypeAlias, TypeVar

# ------------------------------------------------------------------------------------
# TODO: need some to allow string to be passed in : uart_1.write("hello")
AnyReadableBuf: TypeAlias = bytearray | array | memoryview | bytes | Incomplete
AnyWritableBuf: TypeAlias = bytearray | array | memoryview | Incomplete
