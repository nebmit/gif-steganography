from typing import List

from PIL import Image, ImageSequence


def _read_frames(filename: str) -> List[Image.Image]:
    with Image.open(filename) as img:
        return [frame.copy().convert("RGB") for frame in ImageSequence.Iterator(img)]

def _write_frames(frames: List[Image.Image], output_filename: str) -> None:
    rgb_frames = [frame.convert("RGB") for frame in frames]  # Convert each frame to RGB
    rgb_frames[0].save(output_filename, save_all=True, append_images=rgb_frames[1:], loop=0)

def _get_rgb_from_pixel(pixel):
    if(type(pixel) == int):
        raise ValueError("Pixel value is an integer")
    elif(type(pixel) == tuple):
        if len(pixel) == 3:
            return pixel
        elif len(pixel) == 4:
            return pixel[0:3]
    raise ValueError("Unknown pixel value")

def _extract_data_from_frame(frame: Image.Image) -> str:
    width, height = frame.size
    pixels = frame.load()
    binary_data = ""

    for y in range(height):
        for x in range(width):
            try:
                r, g, b = _get_rgb_from_pixel(pixels[x, y])
            except ValueError:
                continue

            # Extract bits from the red, green, and blue components
            bits = [r & 1, g & 1, b & 1]
            bit = set(bits).pop() # Get the majority vote

            binary_data += str(bit)
            
    return binary_data

def _embed_data_in_frame(frame: Image.Image, data: str) -> Image.Image:
    width, height = frame.size
    pixels = frame.load()

    data_index = 0

    for y in range(height):
        for x in range(width):
            try:
                r, g, b = _get_rgb_from_pixel(pixels[x, y])
            except ValueError:
                continue

            r = r & ~1 | int(data[data_index])
            g = g & ~1 | int(data[data_index])
            b = b & ~1 | int(data[data_index])

            data_index += 1

            pixels[x, y] = (r, g, b)

    return frame
