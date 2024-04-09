import os

import pytest

from gif_steganography import SteganographyMethod, decode, encode

GIF_FILES = ["dark.gif", "small.gif"]
INPUT_DIR = os.path.join(os.path.dirname(__file__), "data", "input")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "data", "output.gif")
MODE = SteganographyMethod.CSHIFT
PASSPHRASE = "password"
PAYLOAD = "Secret message."


@pytest.mark.parametrize("gif_file", GIF_FILES)
def test_encode_decode(gif_file):
    input_path = os.path.join(INPUT_DIR, gif_file)
    encode(input_path, OUTPUT_PATH, PAYLOAD, mode=MODE)

    message, _ = decode(OUTPUT_PATH, mode=MODE)
    assert message == PAYLOAD

    # Remove the output file
    os.remove(OUTPUT_PATH)


@pytest.mark.parametrize("gif_file", GIF_FILES)
def test_encode_decode_encrypted(gif_file):
    input_path = os.path.join(INPUT_DIR, gif_file)
    encode(
        input_path,
        OUTPUT_PATH,
        PAYLOAD,
        passphrase=PASSPHRASE,
        mode=MODE,
    )

    message, _ = decode(OUTPUT_PATH, passphrase=PASSPHRASE, mode=MODE)
    assert message == PAYLOAD

    # Remove the output file
    os.remove(OUTPUT_PATH)
