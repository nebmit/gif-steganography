import zlib


def compress(data: str) -> bytearray:
    return bytearray(zlib.compress(data.encode()))

def decompress(data: bytearray) -> str:
    return zlib.decompress(bytes(data)).decode()
