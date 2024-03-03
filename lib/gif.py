from PIL import Image, ImageSequence


def read_frames(filename):
    with Image.open(filename) as img:
        return [frame.copy().convert("RGB") for frame in ImageSequence.Iterator(img)]

def write_frames(frames, output_filename):
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

def extract_data_from_frame(frame):
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

def embed_data_in_frame(frame, data):
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
