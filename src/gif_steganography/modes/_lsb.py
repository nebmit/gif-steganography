from ..lib._gif import _get_rgb_from_pixel
from PIL import Image


def _extract_data_from_frame_lsb(frame: Image.Image) -> str:
    width, height = frame.size
    pixels = frame.load()
    binary_data = ""

    for y in range(height):
        for x in range(width):
            try:
                r, g, b = _get_rgb_from_pixel(pixels[x, y])
            except ValueError:
                # Skip if the pixel is not RGB
                continue

            # Extract bits from the red, green, and blue components
            bits = [r & 1, g & 1, b & 1]
            bit = set(bits).pop()  # Get the majority vote

            binary_data += str(bit)

    return binary_data


def _embed_data_in_frame_lsb(frame: Image.Image, data: str) -> Image.Image:
    width, height = frame.size
    pixels = frame.load()

    data_index = 0

    for y in range(height):
        for x in range(width):
            try:
                r, g, b = _get_rgb_from_pixel(pixels[x, y])
            except ValueError:
                # Skip if the pixel is not RGB
                continue

            # Triple parity bit encoding
            r = r & ~1 | int(data[data_index])
            g = g & ~1 | int(data[data_index])
            b = b & ~1 | int(data[data_index])

            data_index += 1

            pixels[x, y] = (r, g, b)
