# GIF Steganography

## Overview

This project implements GIF steganography using the Least Significant Bit (LSB) technique, coupled with additional layers of security and integrity verification. It enables the encoding of secret messages into GIF images and the decoding of these messages from the images, ensuring the message's secrecy and integrity through encryption, compression, and error correction.

### Key Features

- **Encryption**: Utilizes Fernet symmetric encryption to secure messages.
- **Compression**: Compresses data before encoding to maximize the payload.
- **Error Correction**: Employs Reed-Solomon error correction to enhance data recovery even from partially corrupted GIFs.
- **LSB Steganography**: Uses the Least Significant Bit method to hide data within the GIF frames without noticeable changes to the image.

## Project Structure

- `src/`: Contains the main project files.
- `src/gif_steganography/cli.py`: Command-line interface for encoding and decoding messages.
- `src/gif_steganography/decode.py`: Script to decode messages from GIFs.
- `src/gif_steganography/encode.py`: Script to encode messages into GIFs.
- `src/gif_steganography/lib/`: Contains modules for compression, encryption, error correction, and file operations.
- `src/gif_steganography/modes/`: Contains the encoding and decoding logic for the GIF steganography.


## Installation

Install directly from PyPI with Python 3.x:

```bash
pip install gif-steganography
```

This command installs `gif-steganography` and its dependencies, making it ready for immediate use.


## Usage

This package provides a command-line interface for encoding and decoding secret messages within GIF images using steganography. Ensure the package is installed in your environment to access these features directly from your terminal.

### Encoding Data into a GIF

To encode data into a GIF image, you can use the command-line interface directly. You will need to specify the input GIF file, the output file name for the encoded GIF, the secret message you wish to encode, and a passphrase for encryption.

```bash
gif-steganography encode <input.gif> <output.gif> "Secret Message" "YourPassphrase" --nsym 10
```

- `--nsym` is an optional argument that specifies the Reed-Solomon error correction factor, enhancing the durability of the encoded data against image alterations. The default value is 10.

### Decoding Data from a GIF

To decode a secret message from a GIF image, simply use the decode functionality provided by the command-line interface. Input the GIF file that contains the encoded message and the passphrase that was used for encoding.

```bash
gif-steganography decode <encoded.gif> "YourPassphrase" --nsym 10
```

- Ensure that the `--nsym` value matches the one used during the encoding process for successful decryption.

These commands allow you to seamlessly encode and decode messages within GIF images right from your terminal, leveraging the steganographic capabilities of the package without direct interaction with the Python scripts.

## License

This project is released under the MIT License. See the `LICENSE` file for more details.
