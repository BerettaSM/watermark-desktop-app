import io
import os
from enum import Enum

from PIL import Image, ImageTk, UnidentifiedImageError

SIZE_PROPORTION = .3
IMG_HEIGHT = 150
IMG_WIDTH = 250


def folder_contains_images(path: str = '.'):

    path = os.path.abspath(path)

    if not os.path.isdir(path):
        return False

    files = os.listdir(path)

    if not files:
        return False

    for file in files:

        if '.' not in file:
            # Probably a directory or irrelevant file
            continue

        full_file_path = os.path.join(path, file)

        is_an_image = is_valid_image(full_file_path)

        if is_an_image:
            return True

    return False


def get_resized_image(image: Image, max_width=IMG_WIDTH, max_height=IMG_HEIGHT):

    """Generates a resized image within max_width and max_height."""

    width, height = image.size

    # If image is within both max_width and max_height, there's no need to resize
    if width <= max_width and height <= max_height:
        return image

    # If width is greater than max, calculate both height and width according to ratio.
    if width > max_width:
        ratio = max_width / width
        height = int(ratio * height)
        width = int(ratio * width)

    # If height is still greater than max, recalculate height and width.
    if height > max_height:
        ratio = max_height / height
        height = int(ratio * height)
        width = int(ratio * width)

    resized_image = image.resize((width, height))
    return resized_image


def get_resized_photo_image(path: str = None, bytes_: bytes = None):

    if path is None and bytes_ is None:
        raise ValueError('path or bytes_must be provided')

    if path:
        # Reading an image from a path string
        resized_image = get_resized_image(Image.open(path))

    else:
        # Reading an image from images.py, which is set in bytes
        resized_image = get_resized_image(Image.open(io.BytesIO(bytes_)))

    return ImageTk.PhotoImage(resized_image)


def generate_watermarked_image(target: Image,
                               watermark: Image,
                               watermark_position: str,
                               miniature: bool = False):

    position = Position(watermark_position)
    target_image = target.copy()
    t_width, t_height = target.size

    if miniature:
        resized_watermark = get_resized_image(
            watermark,
            t_width * SIZE_PROPORTION,
            t_height * SIZE_PROPORTION
        )

    else:
        resized_watermark = get_resized_image(watermark, t_width, t_height)

    r_width, r_height = resized_watermark.size

    # delta_width and delta_height position the image on bottom right, by default
    delta_width, delta_height = int(t_width - r_width), int(t_height - r_height)

    if position == Position.CENTER:
        delta_width, delta_height = int(delta_width / 2), int(delta_height / 2)

    elif position == Position.TOP_LEFT:
        delta_width = delta_height = 0

    elif position == Position.BOTTOM_LEFT:
        delta_width = 0

    elif position == Position.TOP_RIGHT:
        delta_height = 0

    try:
        # Image has transparency data
        target_image.paste(resized_watermark, (delta_width, delta_height), resized_watermark)

    except ValueError:
        # Image has no transparency
        target_image.paste(resized_watermark, (delta_width, delta_height))

    return target_image


def is_valid_image(path: str):

    try:
        Image.open(path)

    except (FileNotFoundError, UnidentifiedImageError, PermissionError):
        return False

    return True


class Position(Enum):

    CENTER = 'center'
    TOP_LEFT = 'top-left'
    BOTTOM_LEFT = 'bot-left'
    TOP_RIGHT = 'top-right'
    BOTTOM_RIGHT = 'bot-right'
