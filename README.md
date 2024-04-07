# GIF Steganography

## Overview

This project implements GIF steganography using the Least Significant Bit (LSB) technique, coupled with additional layers of security and integrity verification. It enables the encoding of secret messages into GIF images and the decoding of these messages from the images, ensuring the message's secrecy and integrity through encryption, compression, and error correction.

## Installation

```bash
pip install gif-steganography
```
Requires Python 3.10^. Installs the package and all necessary dependencies.

## Usage

### CLI

#### Encode a Message

```bash
gif-steganography encode <input.gif> <output.gif> "Secret Message" "Passphrase" [--nsym 10]
```
- `--nsym` (optional): Sets the Reed-Solomon error correction level. Default is 10.

#### Decode a Message

```bash
gif-steganography decode <encoded.gif> "Passphrase" [--nsym 10]
```
- `--nsym` must match the encoding setting for successful decryption.

### Programmatic Usage

Beyond the command-line interface, `gif-steganography` also provides direct API access for integrating steganographic functionalities into Python scripts.

#### Basic Encoding and Decoding

Embed and retrieve messages programmatically:

```python
from gif_steganography import encode, decode

# Embed a message
encode("input.gif", "output.gif", "Hello, world!")

# Retrieve a message
message, _ = decode("output.gif")
print(message)  # Output: Hello, world!
```

#### Secure Encoding and Decoding

For added security, use encryption with your messages:

```python
from gif_steganography import encode, decode

# Securely embed a message
encode("input.gif", "output.gif", "Hello, world!", passphrase="password")

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
