from enum import Enum, auto

from . import exceptions
from .decode import decode, decode_encrypted
from .encode import encode, encode_encrypted


class SteganographyMethod(Enum):
    LSB = auto()
    CSHIFT = auto()
