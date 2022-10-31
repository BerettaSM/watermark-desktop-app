import platform
import os
import re
from PIL import Image, UnidentifiedImageError
from tkinter import messagebox

WATERMARK_TO_TARGET_PROPORTION = .3
TITLE_FONT = ('Arial', 30)
ERROR_MESSAGE = """Couldn't open the image.

It's either in an invalid format or currently in a directory that requires privilege.
"""


def get_user_desktop():
    user_os = platform.system()
    if user_os == 'Windows':
        return os.path.join(os.environ['USERPROFILE'], 'Desktop')
    elif user_os == 'Darwin' or user_os == 'Linux':
        return os.path.join(os.path.expanduser('~'), 'Desktop')
    else:
        return ''


def generate_watermarked_image(target: Image, watermark: Image, position: str):

    target_image = target.copy()
    t_width, t_height = target.size

    if position != 'full':
        resized_watermark: Image = get_resized_image(watermark,
                                                     t_width * WATERMARK_TO_TARGET_PROPORTION,
                                                     t_height * WATERMARK_TO_TARGET_PROPORTION)

    else:
        resized_watermark: Image = get_resized_image(watermark, t_width, t_height)

    r_width, r_height = resized_watermark.size

    delta_width, delta_height = int(t_width - r_width), int(t_height - r_height)

    if position in ('full', 'center'):

        delta_width, delta_height = int(delta_width / 2), int(delta_height / 2)

    else:

        if position == 'top-left':
            delta_width = delta_height = 0

        elif position == 'bottom-left':
            delta_width = 0

        elif position == 'top-right':
            delta_height = 0

    target_image.paste(resized_watermark, (delta_width, delta_height))

    return target_image


def get_resized_image(image: Image, max_width=500, max_height=300):

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


def invalid_messagebox():
    messagebox.showerror(title='Error', message=ERROR_MESSAGE)


def is_valid_image(path):
    try:
        Image.open(path)
    except (FileNotFoundError, UnidentifiedImageError, PermissionError):
        return False
    return True


def remove_curly_braces(path):
    regex = re.compile(r'[{}]')
    return regex.sub('', path)
