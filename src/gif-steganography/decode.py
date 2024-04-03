import argparse
from collections import Counter
from typing import List, Tuple

from _exceptions import CorruptDataError, InvalidPassphraseError
from cryptography.fernet import InvalidToken
from lib._compression import _decompress
from lib._ecc import _rs_decode_from_binary
from lib._encryption import _decrypt_message
from lib._gif import _read_frames_as_rgb
from modes._lsb import _extract_data_from_frame_lsb
from reedsolo import ReedSolomonError


def decode(input_filename: str, nsym: int) -> Tuple[str, bool]:
    """
    Decode the hidden message from a GIF file.

    Args:
        input_filename (str): Path to the input GIF file.
        nsym (int): Factor for error correction.

    Returns:
        Tuple[str, bool]: A tuple containing the decoded message and a boolean indicating if the message is corrupt.
    """
    frames = _read_frames_as_rgb(input_filename)

    messages: List[str] = []
    is_corrupt: bool = False
    
    for frame in frames:
        # Extract the binary data from the frame
        binary_data: str = _extract_data_from_frame_lsb(frame)
        if len(binary_data) == 0:
            continue # An empty frame could exist if it's a palette frame

        # Decode the Reed-Solomon encoded data
        try:
            data_bytes: bytes = _rs_decode_from_binary(binary_data, nsym)
            data: str = _decompress(data_bytes)

            messages.append(data)
        except ReedSolomonError:
            is_corrupt = True

    if len(messages) == 0:
        return "", is_corrupt
    
    if len(set(messages)) != 1:
        # The extracted messages are not all the same. We can attempt to recover it
        recovered_data: str = ""
        longest_element: str = max(messages, key=len)
        for i in range(len(longest_element)):
            characters: List[str] = [frame[i] if i < len(frame) else "" for frame in messages]
            majority_vote: str = Counter(characters).most_common(1)[0][0]
            recovered_data += majority_vote
        return recovered_data, True

    return messages[0], is_corrupt

def decode_encrypted(input_filename: str, passphrase: str, nsym: int) -> Tuple[str, bool]:
    """
    Decode and decrypt the hidden message from an encrypted GIF file.

    Args:
        input_filename (str): Path to the input GIF file.
        passphrase (str): Passphrase to be used for decoding.
        nsym (int): Factor for error correction.

    Raises:
        ValueError: If the message is corrupt or the passphrase is incorrect.

    Returns:
        Tuple[str, bool]: A tuple containing the decoded and decrypted message and a boolean indicating if the message is corrupt.
    """
    encrypted_message, is_corrupt = decode(input_filename, nsym)
    try:
        data = _decrypt_message(encrypted_message, passphrase)
        return data, is_corrupt
    except InvalidToken:
        if is_corrupt:
            raise CorruptDataError("Decryption failed. The message appears to be corrupted, which may affect its integrity. This failure could be due to the corruption or an incorrect passphrase.")
        raise InvalidPassphraseError("Decryption failed. This is likely due to an incorrect passphrase.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decode text from a GIF.")
    parser.add_argument("input_file", type=str, help="Path to the input GIF file.")
    parser.add_argument("passphrase", type=str, help="Passphrase to be used for decoding.")
    parser.add_argument("--nsym", type=int, default=10, help="Factor for error correction (default: 10)")

    args = parser.parse_args()

    encrypted_message, is_corrupt = decode(args.input_file, args.nsym)

    try:
        data = _decrypt_message(encrypted_message, args.passphrase)
        if is_corrupt:
            print("\033[93mWarning: The message may have been partially or fully corrupted. "
                "While decryption was successful, the integrity of the data cannot be guaranteed.\033[0m\n")
        print(data)
    except InvalidToken:
        if is_corrupt:
            print("\033[91mError: Decryption failed. The message appears to be corrupted, which may affect its integrity. "
                "This failure could be due to the corruption or an incorrect passphrase.\033[0m")
        else:
            print("\033[91mError: Decryption failed. This is likely due to an incorrect passphrase.\033[0m")
        exit(1)
