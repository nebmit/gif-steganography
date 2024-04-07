import argparse

from .common import CorruptDataError, InvalidPassphraseError
from .decode import decode
from .encode import encode


def main():
    parser = argparse.ArgumentParser(description="GIF Steganography Tool")
    subparsers = parser.add_subparsers(dest="command")

    # Add arguments for encode command
    encode_parser = subparsers.add_parser("encode", help="Encode data into a GIF")
    encode_parser.add_argument(
        "input_file", type=str, help="Path to the input GIF file."
    )
    encode_parser.add_argument(
        "output_file", type=str, help="Path to the output GIF file."
    )
    encode_parser.add_argument(
        "text", type=str, help="Text data to be encoded into the GIF."
    )
    encode_parser.add_argument(
        "passphrase", type=str, help="Passphrase to be used for encoding."
    )
    encode_parser.add_argument(
        "--nsym", type=int, default=10, help="Factor for error correction (default: 10)"
    )

    # Add arguments for decode command
    decode_parser = subparsers.add_parser("decode", help="Decode data from a GIF")
    decode_parser.add_argument(
        "input_file", type=str, help="Path to the input GIF file."
    )
    decode_parser.add_argument(
        "passphrase", type=str, help="Passphrase to be used for decoding."
    )
    decode_parser.add_argument(
        "--nsym", type=int, default=10, help="Factor for error correction (default: 10)"
    )

    args = parser.parse_args()

    if args.command == "encode":
        encode(
            args.input_file,
            args.output_file,
            args.text,
            args.passphrase,
            args.nsym,
            passphrase=args.passphrase,
        )
    elif args.command == "decode":
        try:
            data, is_corrupt = decode(
                args.input_file, args.passphrase, args.nsym, passphrase=args.passphrase
            )
            if is_corrupt:
                print(
                    "\033[93mWarning: The message may have been partially or fully corrupted. "
                    "While decryption was successful, the integrity of the data cannot be guaranteed.\033[0m\n"
                )
            print(data)
        except CorruptDataError:
            print(
                "\033[91mError: Decryption failed. The message appears to be corrupted, which may affect its integrity. "
                "This failure could be due to the corruption or an incorrect passphrase.\033[0m"
            )
            exit(1)
        except InvalidPassphraseError:
            print(
                "\033[91mError: Decryption failed. This is likely due to an incorrect passphrase.\033[0m"
            )
            exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
