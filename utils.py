import platform
import os
import re
from PIL import Image, UnidentifiedImageError
from tkinter import messagebox

TITLE_FONT = ('Arial', 30)

ERROR_MESSAGE = """Couldn't open the image.

It's either in an invalid format or currently in a directory that requires privilege.
"""


def invalid_messagebox():
    messagebox.showerror(title='Error', message=ERROR_MESSAGE)


def get_user_desktop():
    user_os = platform.system()
    if user_os == 'Windows':
        return os.path.join(os.environ['USERPROFILE'], 'Desktop')
    elif user_os == 'Darwin' or user_os == 'Linux':
        return os.path.join(os.path.expanduser('~'), 'Desktop')
    else:
        return ''


def get_resized_image(image: Image, max_width=500, max_height=300):
    width, height = image.size

    if width <= max_width and height <= max_height:
        return image

    if width > max_width:
        ratio = max_width / width
        height = int(ratio * height)
        width = int(ratio * width)

    if height > max_height:
        ratio = max_height / height
        height = int(ratio * height)
        width = int(ratio * width)

    resized_image = image.resize((width, height))
    return resized_image


def remove_curly_braces(path):
    regex = re.compile(r'[{}]')
    return regex.sub('', path)


def is_valid_image(path):
    try:
        Image.open(path)
    except (FileNotFoundError, UnidentifiedImageError, PermissionError):
        return False
    return True
