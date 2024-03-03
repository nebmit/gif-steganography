import argparse
from collections import Counter

from reedsolo import ReedSolomonError

from lib.compression import decompress
from lib.ecc import rs_decode_from_binary
from lib.gif import extract_data_from_frame, read_frames


def decode(input_filename, nsym):
    frames = read_frames(input_filename)

    messages = []
    is_corrupt = False
    
    for frame in frames:
        # Extract the binary data from the frame
        binary_data = extract_data_from_frame(frame)
        if len(binary_data) == 0:
            continue # An empty frame could exist if it's a palette frame

        # Decode the Reed-Solomon encoded data
        try:
            data_bytes = rs_decode_from_binary(binary_data, nsym)
            data = decompress(data_bytes)

            messages.append(data)
        except ReedSolomonError:
            is_corrupt = True

    if len(messages) == 0:
        return "", is_corrupt
    
    if len(set(messages)) != 1:
        # The extracted messages are not all the same. We can attempt to recover it
        recovered_data = ""
        longest_element = max(messages, key=len)
        for i in range(len(longest_element)):
            characters = [frame[i] if i < len(frame) else "" for frame in messages]
            majority_vote = Counter(characters).most_common(1)[0][0]
            recovered_data += majority_vote
        return recovered_data, True

    return messages[0], is_corrupt
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decode text from a GIF.")
    parser.add_argument("input_file", type=str, help="Path to the input GIF file.")
    parser.add_argument("--nsym", type=int, default=10, help="Factor for error correction (default: 10)")

    args = parser.parse_args()

    message, is_corrupt = decode(args.input_file, args.nsym)

    if is_corrupt:
        print("\033[93mNotice: Message data has experienced partial or total corruption. "
               "Recovery attempts have been executed, but the integrity "
               "of the recovered data cannot be fully assured.\n\033[0m")
    
    print(message)
