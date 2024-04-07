import logging
from collections import Counter
from typing import List, Tuple

from cryptography.fernet import InvalidToken
from reedsolo import ReedSolomonError

from .common import CorruptDataError, InvalidPassphraseError, SteganographyMethod
from .lib._compression import _decompress
from .lib._ecc import _rs_decode_from_binary
from .lib._encryption import _decrypt_message
from .lib._gif import _read_frames_as_rgb
from .modes._lsb import _extract_data_from_frame_lsb


def decode(
    input_filename: str,
    mode: SteganographyMethod = SteganographyMethod.LSB,
    nsym: int = 10,
    passphrase: str | None = None,
) -> Tuple[str | bytes, bool]:
    """
    Decode the hidden message from a GIF file.

    Args:
        input_filename (str): Path to the input GIF file.
        mode (SteganographyMethod): Steganography method to use.
        nsym (int): Factor for error correction.
        passphrase (str): Passphrase to be used for decoding.

    Raises:
        CorruptDataError: If the message is corrupted.
        InvalidPassphraseError: If the passphrase is incorrect.

    Returns:
        Tuple[str, bool]: A tuple containing the decoded message and a boolean indicating if the message is corrupt.
    """
    frames = _read_frames_as_rgb(input_filename)

    messages: List[bytes] = []
    is_corrupt: bool = False

    for frame in frames:
        # Extract the binary data from the frame
        binary_data: str = _extract_data_from_frame_lsb(frame)
        if len(binary_data) == 0:
            continue  # An empty frame could exist if it's a palette frame

        # Decode the Reed-Solomon encoded data
        try:
            data_bytes: bytes = _rs_decode_from_binary(binary_data, nsym)
            data: bytes = _decompress(data_bytes)

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
            characters: List[str] = [
                frame[i] if i < len(frame) else "" for frame in messages
            ]
            majority_vote: str = Counter(characters).most_common(1)[0][0]
            recovered_data += majority_vote
        return recovered_data, True

    # Try to decode the message
    message_bytes = messages[0]

    # Decrypt the message if a passphrase is provided
    if passphrase is not None:
        try:
            data = _decrypt_message(message_bytes, passphrase)
            return data, is_corrupt
        except InvalidToken:
            if is_corrupt:
                raise CorruptDataError(
                    "Decryption failed. The message appears to be corrupted, which may affect its integrity. This failure could be due to the corruption or an incorrect passphrase."
                )
            raise InvalidPassphraseError(
                "Decryption failed. This is likely due to an incorrect passphrase."
            )

    # If the message is encrypted but no passphrase is provided, return the encrypted message
    try:
        message = messages[0].decode()
    except UnicodeDecodeError:
        logging.warning(
            "Unable to decode the message as a string. It might be encrypted. Returning as bytes."
        )
        message = messages[0]

    return message, is_corrupt
