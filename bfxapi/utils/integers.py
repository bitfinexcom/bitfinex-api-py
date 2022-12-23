from typing import cast, TypeVar, Union

from .. exceptions import IntegerUnderflowError, IntegerOverflowflowError

__all__ = [ "Int16", "Int32", "Int45", "Int64" ]

T = TypeVar("T")

class _Int(int):
    def __new__(cls: T, integer: int) -> T:
        assert hasattr(cls, "_BITS"), "_Int must be extended by a class that has a static member _BITS (indicating the number of bits with which to represent the integers)."

        bits = cls._BITS - 1

        min, max = -(2 ** bits), (2 ** bits) - 1

        if integer < min:
            raise IntegerUnderflowError(f"Underflow. Cannot store <{integer}> in {cls._BITS} bits integer. The min and max bounds are {min} and {max}.")

        if integer > max:
            raise IntegerOverflowflowError(f"Overflow. Cannot store <{integer}> in {cls._BITS} bits integer. The min and max bounds are {min} and {max}.")
            
        return cast(T, super().__new__(int, integer))

class Int16(_Int):
    _BITS = 16

int16 = Union[Int16, int]

class Int32(_Int):
    _BITS = 32

int32 = Union[Int32, int]

class Int45(_Int):
    _BITS = 45

int45 = Union[Int45, int]

class Int64(_Int):
    _BITS = 64

int64 = Union[Int64, int]