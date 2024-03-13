import zlib


def compress(data: bytearray) -> bytearray:
    return bytearray(zlib.compress(data))

def decompress(data: bytearray) -> bytearray:
    return zlib.decompress(bytes(data))
