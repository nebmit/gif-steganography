import zlib


def _compress(data: bytearray) -> bytearray:
    return bytearray(zlib.compress(data))


def _decompress(data: bytearray) -> bytearray:
    return zlib.decompress(bytes(data))
