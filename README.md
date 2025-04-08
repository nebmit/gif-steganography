# GIF Steganography

[![Tests](https://github.com/nebmit/gif-steganography/actions/workflows/python-package.yml/badge.svg)](https://github.com/nebmit/gif-steganography/actions/workflows/python-package.yml)
[![PyPI version](https://badge.fury.io/py/gif-steganography.svg)](https://badge.fury.io/py/gif-steganography)
[![Dependencies](https://img.shields.io/librariesio/release/pypi/gif-steganography)](https://libraries.io/pypi/gif-steganography)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python version](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)

## Overview

This project implements GIF steganography using various techniques, coupled with additional layers of security and integrity verification. It enables the encoding of secret messages into GIF images and the decoding of these messages from the images, ensuring the message's secrecy and integrity through encryption, compression, and error correction.

<table>
  <tr>
    <td align="center"><img src="docs/input.gif" alt="Input GIF" width="300"></td>
    <td align="center"><img src="docs/output.gif" alt="Output GIF" width="300"></td>
  </tr>
</table>

One of these GIFs contains a dragon. Can you find it? (Hint: the passphrase is "dragon".)

## Installation

```bash
pip install gif-steganography
```

Requires Python >= 3.10. Installs the package and all necessary dependencies.

## Usage

### Encode a Message

```bash
gif-steganography encode <input.gif> <output.gif> "Secret Message" "Passphrase" [--nsym 10]
```

- `--nsym` (optional): Sets the Reed-Solomon error correction level. Default is 10.

### Decode a Message

```bash
gif-steganography decode <encoded.gif> "Passphrase" [--nsym 10]
```

- `--nsym` must match the encoding setting for successful decryption.

### Programmatic Usage

Beyond the command-line interface, `gif-steganography` also provides direct API access for integrating steganographic functionalities into Python scripts.

#### Basic Encoding and Decoding

Embed and retrieve messages programmatically:

```python
from gif_steganography import SteganographyMethod, decode, encode

# Embed a message
encode("input.gif", "output.gif", "Hello, world!", mode=SteganographyMethod.LSB)

# Retrieve a message
message, _ = decode("output.gif")
print(message)  # Output: Hello, world!
```

#### Secure Encoding and Decoding

For added security, use encryption with your messages:

```python
from gif_steganography import SteganographyMethod, decode, encode

# Securely embed a message
encode("input.gif", "output.gif", "Hello, world!", passphrase="password", mode=SteganographyMethod.CSHIFT)

# Securely retrieve a message
message, _ = decode("output.gif", passphrase="password")
print(message)  # Output: Hello, world!
```

## Project Structure

- `src/`: Core project files.
- `cli.py`: Command-line interface.
- `encode.py`/`decode.py`: Encoding and decoding scripts.
- `lib/`: Compression, encryption, and utility modules.
- `modes/`: Core steganography logic.

## License

Distributed under the MIT License. See `LICENSE` for more information.
