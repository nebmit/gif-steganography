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
- `src/gif-steganography/decode.py`: Script to decode messages from GIFs.
- `src/gif-steganography/encode.py`: Script to encode messages into GIFs.
- `src/gif-steganography/lib/`: Contains modules for compression, encryption, error correction, and GIF manipulation.

## Installation

Ensure you have Python 3.x installed on your system. Clone this repository, then install the required dependencies by running:

```bash
pip install -r requirements.txt
```

## Usage

### Encoding Data into a GIF

To encode data into a GIF image, use the `encode.py` script. You'll need to provide the input GIF file, the output GIF file name, the text you wish to encode, and a passphrase for encryption.

```bash
python src/gif-steganography/encode.py <input.gif> <output.gif> "Secret Message" "YourPassphrase" --nsym 10
```

- `--nsym` is optional and specifies the Reed-Solomon error correction factor (default is 10).

### Decoding Data from a GIF

To decode the secret message from a GIF image, use the `decode.py` script. Provide the GIF file containing the encoded message and the passphrase used for encoding.

```bash
python src/gif-steganography/decode.py <encoded.gif> "YourPassphrase" --nsym 10
```

- `--nsym` must match the value used during encoding.

## License

This project is released under the MIT License. See the `LICENSE` file for more details.
