import os
import platform
import re
import webbrowser
from tkinter import messagebox


def get_user_desktop():

    user_os = platform.system()

    if user_os == 'Windows':
        return os.path.join(os.environ['USERPROFILE'], 'Desktop').replace('\\', '/')

    elif user_os == 'Darwin' or user_os == 'Linux':
        return os.path.join(os.path.expanduser('~'), 'Desktop')

    else:
        return 'Choose destiny folder'


def about_messagebox():

    open_git = messagebox.askyesno(title='About', message="""Created by Ramon Saviato.
    

Email: ramonsaviato@hotmail.com

GitHub: BerettaSM

View profile on GitHub?""")

    if open_git:
        open_github()


def invalid_image_messagebox():

    messagebox.showerror(title='Error', message="""Couldn't open the image.

It's either in an invalid format or currently in a directory that requires privilege.
""")


def invalid_dir_messagebox():

    messagebox.showerror(title='Error', message='Not a valid directory.')


def open_github():

    webbrowser.open('https://github.com/BerettaSM')


def processed_images_messagebox(n: int):

    messagebox.showinfo(title='Done', message=f'Result: {n} images watermarked.')


def remove_curly_braces(path: str):

    regex = re.compile(r'[{}]')

    return regex.sub('', path)
