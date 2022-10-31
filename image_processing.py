from PIL import Image, UnidentifiedImageError
from enum import Enum


SIZE_PROPORTION = .3
IMG_HEIGHT = 300
IMG_WIDTH = 500


def is_valid_image(path):
    try:
        Image.open(path)
    except (FileNotFoundError, UnidentifiedImageError, PermissionError):
        return False
    return True


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


def generate_watermarked_image(target: Image,
                               watermark: Image,
                               position: str,
                               miniature: bool = False):

    position = Position(position)
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


class Position(Enum):

    CENTER = 'center'
    TOP_LEFT = 'top-left'
    BOTTOM_LEFT = 'bottom-left'
    TOP_RIGHT = 'top-right'
    BOTTOM_RIGHT = 'bottom-right'
