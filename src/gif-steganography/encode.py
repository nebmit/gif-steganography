import argparse
import tempfile
from typing import List

from lib._compression import _compress
from lib._ecc import _rs_encode_to_binary
from lib._encryption import _encrypt_message
from lib._gif import _embed_data_in_frame, _read_frames, _write_frames
from PIL import Image


def encode(input_filename: str, output_filename: str, data: bytes, nsym: int) -> None:
    """
    Encode data into a GIF file.

    Args:
        input_filename (str): Path to the input GIF file.
        output_filename (str): Path to the output GIF file.
        data (bytes): Data to be encoded into the GIF.
        nsym (int): Factor for error correction.

    Raises:
        ValueError: If the input data is too large to fit in the input file.

    Returns:
        None
    """
    frames: List[Image.Image] = _read_frames(input_filename)

    # The save operation changes a GIF's palette, so we need to re-read it
    with tempfile.NamedTemporaryFile(suffix='.gif') as temp_file:
        temp_filename: str = temp_file.name
        _write_frames(frames, temp_filename)
        frames = _read_frames(temp_filename)

    if frames:
        data_bytes: bytes = _compress(data)

        # Calculate the total available space in the smallest frame
        smallest_frame: Image.Image = min(frames, key=lambda frame: frame.size[0] * frame.size[1])
        total_bits: int = smallest_frame.size[0] * smallest_frame.size[1] * 3
        total_bytes: int = total_bits // 8  # Convert bits to bytes

        if len(data_bytes) > total_bytes:
            raise ValueError("Input data too large to fit in the input file.")

        # Pad the data with null bytes to fill the frame
        filler_bytes: bytes = b'\x00' * (total_bytes - len(data_bytes) - nsym)

        # Encode the data with the Reed-Solomon codec
        binary_data: bytes = _rs_encode_to_binary(data_bytes + filler_bytes, nsym)

        # Embed the data in the frames
        modified_frames: List[Image.Image] = [_embed_data_in_frame(frame, binary_data) for frame in frames]

        _write_frames(modified_frames, output_filename)

def encode_encrypted(input_filename: str, output_filename: str, message: str, passphrase: str, nsym: int) -> None:
    """
    Encode an encrypted message into a GIF file.

    Args:
        input_filename (str): Path to the input GIF file.
        output_filename (str): Path to the output GIF file.
        message (str): Message to be encrypted and encoded into the GIF.
        passphrase (str): Passphrase to be used for encryption.
        nsym (int): Factor for error correction.

    Raises:
        ValueError: If the input data is too large to fit in the input file.

    Returns:
        None
    """
    encrypted_message: bytes = _encrypt_message(message, passphrase)
    encode(input_filename, output_filename, encrypted_message, nsym)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encode text into a GIF.")
    parser.add_argument("input_file", type=str, help="Path to the input GIF file.")
    parser.add_argument("output_file", type=str, help="Path to the output GIF file.")
    parser.add_argument("text", type=str, help="Text data to be encoded into the GIF.")
    parser.add_argument("passphrase", type=str, help="Passphrase to be used for encoding.")
    parser.add_argument("--nsym", type=int, default=10, help="Factor for error correction (default: 10)")

    args = parser.parse_args()

    try:
        encode_encrypted(args.input_file, args.output_file, args.text, args.passphrase, args.nsym)
    except ValueError as e:
        print(e)
