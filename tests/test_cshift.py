import os

import pytest

from gif_steganography import SteganographyMethod, decode, encode

GIF_FILES = ["dark.gif", "transparency.gif", "forest.gif", "capybara.gif"]
INPUT_DIR = os.path.join(os.path.dirname(__file__), "data", "input")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "data", "output.gif")
MODE = SteganographyMethod.CSHIFT
PASSPHRASE = "password"
PAYLOAD = "Secret message."
LARGE_PAYLOAD = """
                                   / \\  //\\
                    |\\___/|      /   \\//  \\\\\\
                    /O  O  \\__  /    //  | \\ \\    
                   /     /  \\/_/    //   |  \\  \\  
                   @_^_@'/   \\/_   //    |   \\   \\ 
                   //_^_/     \\/_ //     |    \\    \\
                ( //) |        \\///      |     \\     \\
              ( / /) _|_ /   )  //       |      \\     _\\
            ( // /) '/,_ _ _/  ( ; -.    |    _ _\\.-~        .-~~~^-.
          (( / / )) ,-{        _      `-.|.-~-.           .~         `.
         (( // / ))  '/\\      /                 ~-. _ .-~      .-~^-.  \\
         (( /// ))      `.   {            }                   /      \\  \\
          ((/ ))     .----~-.\\        \\-'                 .~         \\  `. \\^-.
                     ///.----..>        \\             _ -~             `.  ^-`  ^-_
                       ///-._ _ _ _ _ _ _}^ - - - - ~                     ~-- ,.-~
                                                                          /.-~
"""


@pytest.mark.parametrize("gif_file", GIF_FILES)
@pytest.mark.parametrize("payload", [PAYLOAD, LARGE_PAYLOAD])
def test_encode_decode(gif_file, payload):
    input_path = os.path.join(INPUT_DIR, gif_file)
    encode(input_path, OUTPUT_PATH, payload, mode=MODE)

    message, _ = decode(OUTPUT_PATH, mode=MODE)
    assert message == payload

    # Remove the output file
    os.remove(OUTPUT_PATH)


@pytest.mark.parametrize("gif_file", GIF_FILES)
@pytest.mark.parametrize("payload", [PAYLOAD, LARGE_PAYLOAD])
def test_encode_decode_encrypted(gif_file, payload):
    input_path = os.path.join(INPUT_DIR, gif_file)
    encode(
        input_path,
        OUTPUT_PATH,
        payload,
        passphrase=PASSPHRASE,
        mode=MODE,
    )

    message, _ = decode(OUTPUT_PATH, passphrase=PASSPHRASE, mode=MODE)
    assert message == payload

    # Remove the output file
    os.remove(OUTPUT_PATH)
