from typing import List

from PIL import Image, ImageSequence


def _read_frames_as_rgb(filename: str) -> List[Image.Image]:
    with Image.open(filename) as img:
        frames = [frame.convert("RGB") for frame in ImageSequence.Iterator(img)]
        return frames


def _write_frames_as_rgb(frames: List[Image.Image], output_filename: str) -> None:
    rgb_frames = [frame.convert("RGB") for frame in frames]  # Convert each frame to RGB
    rgb_frames[0].save(
        output_filename, save_all=True, append_images=rgb_frames[1:], loop=0
    )


def _get_rgb_from_pixel(pixel):
    if type(pixel) == int:
        raise ValueError("Pixel value is an integer")
    elif type(pixel) == tuple:
        if len(pixel) == 3:
            return pixel
        elif len(pixel) == 4:
            return pixel[0:3]
    raise ValueError("Unknown pixel value")


def _read_frames_as_p(filename: str) -> Image.Image:
    with Image.open(filename) as img:
        frames = [
            frame.convert("P", palette=Image.ADAPTIVE, colors=256)
            for frame in ImageSequence.Iterator(img)
        ]
        return frames


def _write_frames_as_p(frames: Image.Image, output_filename: str) -> None:
    frames[0].save(output_filename, save_all=True, append_images=frames[1:], loop=0)
