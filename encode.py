import argparse
import tempfile

from lib.compression import compress
from lib.ecc import rs_encode_to_binary
from lib.encryption import encrypt_message
from lib.gif import embed_data_in_frame, read_frames, write_frames


def encode(input_filename, output_filename, data, nsym):
    frames = read_frames(input_filename)

    # The save operation changes a GIF's palette, so we need to re-read it
    with tempfile.NamedTemporaryFile(suffix='.gif') as temp_file:
        temp_filename = temp_file.name
        write_frames(frames, temp_filename)
        frames = read_frames(temp_filename)

    if frames:
        data_bytes = compress(data)

        # Calculate the total available space in the smallest frame
        smallest_frame = min(frames, key=lambda frame: frame.size[0] * frame.size[1])
        total_bits = smallest_frame.size[0] * smallest_frame.size[1] * 3
        total_bytes = total_bits // 8  # Convert bits to bytes

        if len(data_bytes) > total_bytes:
            raise ValueError("Input data too large to fit in the input file.")

        # Pad the data with null bytes to fill the frame
        filler_bytes = b'\x00' * (total_bytes - len(data_bytes) - nsym)

        # Encode the data with the Reed-Solomon codec
        binary_data = rs_encode_to_binary(data_bytes + filler_bytes, nsym)

        # Embed the data in the frames
        modified_frames = [embed_data_in_frame(frame, binary_data) for frame in frames]

        write_frames(modified_frames, output_filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encode text into a GIF.")
    parser.add_argument("input_file", type=str, help="Path to the input GIF file.")
    parser.add_argument("output_file", type=str, help="Path to the output GIF file.")
    parser.add_argument("text", type=str, help="Text data to be encoded into the GIF.")
    parser.add_argument("passphrase", type=str, help="Passphrase to be used for encoding.")
    parser.add_argument("--nsym", type=int, default=10, help="Factor for error correction (default: 10)")

    args = parser.parse_args()

    encrypted_data = encrypt_message(args.text, args.passphrase)
    
    try:
        encode(args.input_file, args.output_file, encrypted_data, args.nsym)
    except ValueError as e:
        print(e)
