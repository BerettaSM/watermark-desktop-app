import os
import platform
import re
from tkinter import messagebox


TITLE_FONT = ('Arial', 18)
SECONDARY_FONT = ('Arial', 14)


def get_user_desktop():
    user_os = platform.system()
    if user_os == 'Windows':
        return os.path.join(os.environ['USERPROFILE'], 'Desktop')
    elif user_os == 'Darwin' or user_os == 'Linux':
        return os.path.join(os.path.expanduser('~'), 'Desktop')
    else:
        return ''


def invalid_messagebox():
    messagebox.showerror(title='Error', message="""Couldn't open the image.

It's either in an invalid format or currently in a directory that requires privilege.
""")


def remove_curly_braces(path):
    regex = re.compile(r'[{}]')
    return regex.sub('', path)
