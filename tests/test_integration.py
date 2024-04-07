import os

from gif_steganography.decode import decode
from gif_steganography.encode import encode


def test_encode_decode():
    input_path = os.path.join(os.path.dirname(__file__), "data", "input.gif")
    output_path = os.path.join(os.path.dirname(__file__), "data", "output.gif")
    encode(input_path, output_path, "Secret message")

    message, _ = decode(output_path)
    assert message == "Secret message"

    # Remove the output file
    os.remove(output_path)


def test_encode_decode_encrypted():
    input_path = os.path.join(os.path.dirname(__file__), "data", "input.gif")
    output_path = os.path.join(os.path.dirname(__file__), "data", "output.gif")
    encode(input_path, output_path, "Secret message", passphrase="password")

    message, _ = decode(output_path, passphrase="password")
    assert message == "Secret message"

    # Remove the output file
    os.remove(output_path)
