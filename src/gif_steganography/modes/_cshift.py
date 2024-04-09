from typing import List, Tuple

from PIL import Image

from ..common import CapacityError, InternalError
from ..lib._ecc import _rs_encode_to_binary, _rs_decode_from_binary


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

    # Replace the pixels with the new color indexes
    pixels = image.load()
    width, height = image.size
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            new_pixel = min(
                range(len(new_colors)),
                key=lambda i: _color_distance(new_colors[i], colors[pixel]),
            )
            pixels[x, y] = new_pixel


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


def _get_color_index(
    colors: List[Tuple[int, int, int]], color: Tuple[int, int, int]
) -> int:
    color_index = -1
    for i, c in enumerate(colors):
        if c == color:
            if color_index != -1:
                raise InternalError(
                    f"Color {color} at index {i} is not unique in the palette."
                )
            color_index = i
    return color_index


def _combine_duplicate_colors(image: Image.Image) -> None:
    colors = _get_colors(image)

    unique_colors = list(set(colors))
    new_palette = [channel for color in unique_colors for channel in color]
    image.putpalette(new_palette)

    # Combine colors that are equal
    pixels = image.load()
    width, height = image.size
    for y in range(height):
        for x in range(width):
            pixels[x, y] = _get_color_index(unique_colors, colors[pixels[x, y]])


def _find_most_used_color(image: Image.Image) -> Tuple[int, Tuple[int, int, int]]:
    colors = _get_colors(image)

    # Count color usage
    color_counts = {i: 0 for i in range(len(colors))}
    for pixel in image.getdata():
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

    # If image supports transparency
    if image.info.get("transparency") is not None:
        transparency = image.info.get("transparency")
        color_that_was_transparent = transparency
        color_that_should_be_transparent = _get_color_index(
            new_colors, color_that_was_transparent
        )
        image.info["transparency"] = color_that_should_be_transparent

    if sum(original_color) == 255 * 3:
        # Since the original color is white, we need to swap
        pixels = image.load()
        width, height = image.size
        for y in range(height):
            for x in range(width):
                if pixels[x, y] == original_color_index:
                    pixels[x, y] = _get_color_index(new_colors, varied_color)
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
    _simplify_palette(image)

    most_used_color_index = _find_most_used_color(image)
    original_color, varied_color = _create_data_pair(image, most_used_color_index)

    # Get the index of the varied color
    colors = _get_colors(image)
    original_color_index = _get_color_index(colors, original_color)
    varied_color_index = _get_color_index(colors, varied_color)

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
    for i, color1 in enumerate(colors):
        for j, color2 in enumerate(colors):
            if i == j:
                continue
            if 1 <= _color_distance(color1, color2) <= 3:
                # The higher color value is the varied color
                if _color_size(color1) > _color_size(color2):
                    varied_color_index = _get_color_index(colors, color1)
                    most_used_color_index = _get_color_index(colors, color2)
                else:
                    most_used_color_index = _get_color_index(colors, color1)
                    varied_color_index = _get_color_index(colors, color2)
                break

    extracted_data = _extract_data(image, most_used_color_index, varied_color_index)

    return extracted_data
