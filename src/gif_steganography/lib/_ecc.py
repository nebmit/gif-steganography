from reedsolo import RSCodec


def _rs_encode_to_binary(data: bytes, nsym: int) -> str:
    rscodec = RSCodec(nsym)
    rs_data = rscodec.encode(data)
    binary_data = "".join(format(byte, "08b") for byte in rs_data)
    return binary_data


def _rs_decode_from_binary(data: str, nsym: int) -> bytes:
    bytes = bytearray(int(data[i : i + 8], 2) for i in range(0, len(data), 8))
    rscodec = RSCodec(nsym)
    decoded_bytes, _, _ = rscodec.decode(bytes)
    return decoded_bytes
