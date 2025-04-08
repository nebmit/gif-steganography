from functools import lru_cache
from typing import List, Tuple

import numpy as np
from PIL import Image

from ..common import CapacityError, InternalError


def _simplify_palette(image: Image.Image) -> None:
    _combine_duplicate_colors(image)
    colors = _get_colors(image)

    # Identify colors within an absolute distance of 2
    colors_to_remove = set()
    colors_by_distance = {}
    for i, color1 in enumerate(colors):
        for j, color2 in enumerate(colors):
            if i == j:
                continue
            if i in colors_to_remove or j in colors_to_remove:
                continue
            colors_by_distance[(i, j)] = _color_distance(color1, color2)
            if _color_distance(color1, color2) <= 2:
                colors_to_remove.add(j)

    # Sort colors by distance
    colors_by_distance = {
        k: v for k, v in sorted(colors_by_distance.items(), key=lambda item: item[1])
    }

    # If the palette is at its maximum size and we're not planning to remove any colors, remove the nearest color
    if len(colors) == 256 and not colors_to_remove:
        colors_to_remove = {k[1] for k in list(colors_by_distance.keys())[:1]}

    # Keep only the colors that are not to be removed
    new_colors = [color for i, color in enumerate(colors) if i not in colors_to_remove]
    new_palette = [channel for color in new_colors for channel in color]

    # Update the image palette
    image.putpalette(new_palette)

    # Precompute the optimal new color for every original palette index
    mapping = [
        min(
            range(len(new_colors)),
            key=lambda i: _color_distance(new_colors[i], orig_color),
        )
        for orig_color in colors
    ]

    # Convert image to a NumPy array (assumes image is in mode 'P')
    img_array = np.array(image)
    # Apply the mapping using np.take (mapping should be a sequence of new pixel values)
    new_img_array = np.take(mapping, img_array)

    # Reconstruct the image and update its palette
    image = Image.fromarray(new_img_array.astype("uint8"), mode="P")
    image.putpalette(new_palette)


@lru_cache(maxsize=None)
def _color_distance(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> int:
    return max(abs(c1 - c2) for c1, c2 in zip(color1, color2))


def _color_size(color: Tuple[int, int, int]) -> int:
    return sum(color)


def _get_colors(
    image: Image.Image,
) -> List[Tuple[int, int, int]] | List[Tuple[int, int, int, int]]:
    palette = image.getpalette()
    colors = [tuple(palette[i : i + 3]) for i in range(0, len(palette), 3)]
    return colors


def _build_color_index_map(
    colors: List[Tuple[int, int, int]]
) -> dict[Tuple[int, int, int], int]:
    mapping = {}
    for i, color in enumerate(colors):
        if color in mapping:
            raise InternalError(f"Color {color} appears more than once in the palette.")
        mapping[color] = i
    return mapping


def _combine_duplicate_colors(image: Image.Image) -> None:
    colors = _get_colors(image)

    unique_colors = list(set(colors))
    new_palette = [channel for color in unique_colors for channel in color]
    image.putpalette(new_palette)

    color_index_map = _build_color_index_map(unique_colors)

    # Precompute the lookup: for each index in the original palette,
    # map it to the new palette index.
    lookup = np.array(
        [color_index_map[colors[i]] for i in range(len(colors))], dtype=np.uint8
    )

    # Convert image to a NumPy array (assumes image is in mode "P").
    img_arr = np.array(image)

    # Remap all pixels at once using vectorized indexing.
    new_img_arr = lookup[img_arr]

    # Create a new image from the remapped array.
    new_image = Image.fromarray(new_img_arr, mode="P")
    new_image.putpalette(new_palette)

    # Update the original image in-place.
    image.paste(new_image)


def _find_most_used_color(image: Image.Image) -> Tuple[int, Tuple[int, int, int]]:
    colors = _get_colors(image)

    # Count color usage
    color_counts = {i: 0 for i in range(len(colors))}
    for pixel in image.getdata():
        if pixel not in color_counts:
            # If the pixel color is not in the palette, skip it
            continue
        color_counts[pixel] += 1

    # Find the most used color index
    most_used_color_index = max(color_counts, key=color_counts.get)
    return most_used_color_index


def _create_data_pair(image: Image.Image, original_color_index: int) -> None:
    old_palette = image.getpalette()
    old_colors = _get_colors(image)

    original_color = old_colors[original_color_index]

    # Create the alternative color
    if sum(original_color) == 255 * 3:
        # Since the original color is white, we need to swap
        varied_color = tuple(max(c - 1, 0) for c in original_color)
    else:
        varied_color = tuple(min(c + 1, 255) for c in original_color)

    new_palette = old_palette + [channel for channel in varied_color]

    # Append the new color to the palette
    image.putpalette(new_palette)

    new_colors = _get_colors(image)
    color_index_map = _build_color_index_map(new_colors)

    if sum(original_color) == 255 * 3:
        # Since the original color is white, we need to swap
        pixels = image.load()
        width, height = image.size
        for y in range(height):
            for x in range(width):
                if pixels[x, y] == original_color_index:
                    pixels[x, y] = color_index_map.get(varied_color, -1)
        return varied_color, original_color

    return original_color, varied_color


def _embed_data(
    image: Image.Image, data: str, original_color_index: int, varied_color_index: int
) -> None:
    pixels = image.load()
    width, height = image.size

    data_index = 0
    for y in range(height):
        for x in range(width):
            if data_index >= len(data):
                break  # Stop if we've encoded all the data

            if pixels[x, y] != original_color_index:
                continue  # Skip if the pixel is not the original color

            # Use the original or varied color index to represent 0 or 1
            pixel_color_index = (
                original_color_index if data[data_index] == "0" else varied_color_index
            )
            pixels[x, y] = pixel_color_index

            data_index += 1

    if data_index < len(data):
        print(data_index, len(data))
        raise CapacityError("Not enough space in frame to embed data.")


def _embed_data_in_frame_cshift(image: Image, data: str) -> Image.Image:
    if image.info.get("transparency") is not None:
        transparency = image.info.get("transparency")
        color_that_was_transparent = _get_colors(image)[transparency]

    _simplify_palette(image)

    most_used_color_index = _find_most_used_color(image)
    original_color, varied_color = _create_data_pair(image, most_used_color_index)

    # Get the index of the varied color
    colors = _get_colors(image)
    color_index_map = _build_color_index_map(colors)

    original_color_index = color_index_map.get(original_color, -1)
    varied_color_index = color_index_map.get(varied_color, -1)

    if image.info.get("transparency") is not None:
        mapped_transparency = min(
            range(len(colors)),
            key=lambda i: _color_distance(colors[i], color_that_was_transparent),
        )
        image.info["transparency"] = mapped_transparency

    _embed_data(image, data, original_color_index, varied_color_index)


def _extract_data(
    image: Image, original_color_index: int, varied_color_index: int
) -> str:
    pixels = image.load()
    width, height = image.size

    binary_data = ""
    data_index = 0
    for y in range(height):
        for x in range(width):
            # Determine whether the pixel uses the original or varied color index
            if pixels[x, y] == original_color_index:
                binary_data += "0"
            elif pixels[x, y] == varied_color_index:
                binary_data += "1"
            else:
                continue

            data_index += 1

    return binary_data


def _extract_data_from_frame_cshift(image: Image) -> str:
    _combine_duplicate_colors(image)

    colors = _get_colors(image)
    color_index_map = _build_color_index_map(colors)

    for i, color1 in enumerate(colors):
        for j, color2 in enumerate(colors):
            if i == j:
                continue
            if 1 <= _color_distance(color1, color2) <= 3:
                # The higher color value is the varied color
                if _color_size(color1) > _color_size(color2):
                    varied_color_index = color_index_map.get(color1, -1)
                    most_used_color_index = color_index_map.get(color2, -1)
                else:
                    most_used_color_index = color_index_map.get(color1, -1)
                    varied_color_index = color_index_map.get(color2, -1)
                break

    extracted_data = _extract_data(image, most_used_color_index, varied_color_index)

    return extracted_data
