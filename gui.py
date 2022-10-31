import tkinter as tk
from tkinter import N, S, E, W
from tkinter import ttk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD

from PIL import ImageTk, Image

from pathlib import Path

from utils import get_resized_image, get_user_desktop, is_valid_image, remove_curly_braces, invalid_messagebox
from utils import TITLE_FONT

ERROR_MESSAGE = """Couldn't open the image.

It's either in an invalid format or currently in a directory that requires privilege.
"""


class GUI(ttk.Frame):

    USER_DESKTOP = get_user_desktop()

    def __init__(self, master: TkinterDnD.Tk):

        super().__init__(master=master)

        self.master: TkinterDnD.Tk = master
        self.master.title("Watermark Desktop App")

        self.grid(row=0, column=0)
        self.configure(padding="15 15 15 15")

        self.destiny_path: tk.StringVar | None = None
        self.target_image_path: tk.StringVar | None = None
        self.watermark_image_path: tk.StringVar | None = None

        self.target_drag_zone_wrapper = None
        self.target_drag_zone_wrapper_image = None
        self.target_drag_zone = None
        self.target_drag_zone_background = None

        self.watermark_drag_zone_wrapper = None
        self.watermark_drag_zone_wrapper_image = None
        self.watermark_drag_zone = None
        self.watermark_drag_zone_background = None

        self.preview_zone_wrapper = None
        self.preview_zone_wrapper_image = None
        self.preview_zone = None
        self.preview_zone_background = None

        self.img_width = 500
        self.img_height = 300

        self.create_widgets()
        self.register_event_listeners()

    def create_widgets(self):

        destiny_button = ttk.Button(self, text='Choose destiny', command=self.destiny_folder_browse_event)
        destiny_button.grid(row=0, column=0, sticky=W + E, padx=5, pady=5)

        self.destiny_path = tk.StringVar(value=get_user_desktop())
        destiny_entry = ttk.Entry(self, textvariable=self.destiny_path, state='readonly')
        destiny_entry.grid(row=0, column=1, columnspan=4, sticky=W + E, padx=5, pady=5)

        target_image_button = ttk.Button(self, text='Choose target', command=self.target_img_browse_event)
        target_image_button.grid(row=1, column=0, sticky=W + E, padx=5, pady=5)

        self.target_image_path = tk.StringVar(value='Choose a image target')
        target_image_entry = ttk.Entry(self, textvariable=self.target_image_path, state='readonly')
        target_image_entry.grid(row=1, column=1, columnspan=4, sticky=W + E, padx=5, pady=5)

        watermark_image_button = ttk.Button(self, text='Choose watermark', command=self.watermark_img_browse_event)
        watermark_image_button.grid(row=2, column=0, sticky=W + E, padx=5, pady=5)

        self.watermark_image_path = tk.StringVar(value='Choose a watermark')
        watermark_image_entry = ttk.Entry(self, textvariable=self.watermark_image_path, state='readonly')
        watermark_image_entry.grid(row=2, column=1, columnspan=4, sticky=W + E, padx=5, pady=5)

        target_title_label = ttk.Label(self, text='Target Image', font=TITLE_FONT)
        target_title_label.grid(row=3, column=0, columnspan=5)

        watermark_title_label = ttk.Label(self, text='Your Watermark', font=TITLE_FONT)
        watermark_title_label.grid(row=3, column=5, columnspan=5)

        self.target_drag_zone_wrapper_image = ImageTk.PhotoImage(Image.open('drag_and_drop_background.jpg'))
        self.target_drag_zone_wrapper = tk.Label(self, image=self.target_drag_zone_wrapper_image)
        self.target_drag_zone_wrapper.configure(width=515, height=515)
        self.target_drag_zone_wrapper.grid(row=4, column=0, columnspan=5, padx=7)

        self.target_drag_zone_background = self.get_resized_image('drag_and_drop_front.jpg')
        self.target_drag_zone = tk.Label(self.target_drag_zone_wrapper, image=self.target_drag_zone_background)
        self.target_drag_zone.configure(width=self.img_width, height=self.img_height)
        self.target_drag_zone.grid(row=0, column=0, pady=7, padx=7)

        self.watermark_drag_zone_wrapper_image = ImageTk.PhotoImage(Image.open('drag_and_drop_background.jpg'))
        self.watermark_drag_zone_wrapper = tk.Label(self, image=self.target_drag_zone_wrapper_image)
        self.watermark_drag_zone_wrapper.configure(width=515, height=515)
        self.watermark_drag_zone_wrapper.grid(row=4, column=5, columnspan=5, padx=7)

        self.watermark_drag_zone_background = self.get_resized_image('drag_and_drop_front.jpg')
        self.watermark_drag_zone = tk.Label(self.watermark_drag_zone_wrapper, image=self.watermark_drag_zone_background)
        self.watermark_drag_zone.configure(width=self.img_width, height=self.img_height)
        self.watermark_drag_zone.grid(row=0, column=0, pady=7, padx=7)

        preview_title_label = ttk.Label(self, text='Preview', font=TITLE_FONT)
        preview_title_label.grid(row=3, column=11, columnspan=5)

        self.preview_zone_wrapper_image = ImageTk.PhotoImage(Image.open('drag_and_drop_background.jpg'))
        self.preview_zone_wrapper = tk.Label(self, image=self.preview_zone_wrapper_image)
        self.preview_zone_wrapper.configure(width=515, height=515)
        self.preview_zone_wrapper.grid(row=4, column=11, columnspan=5, padx=7)

        self.preview_zone_background = self.get_resized_image('transparent.png')
        self.preview_zone = tk.Label(self.preview_zone_wrapper, image=self.preview_zone_background)
        self.preview_zone.configure(width=self.img_width, height=self.img_height)
        self.preview_zone.grid(row=0, column=0, pady=7, padx=7)

    def register_event_listeners(self):

        """Register drag and drop events for both images"""

        self.target_drag_zone.drop_target_register(DND_FILES)
        self.target_drag_zone.dnd_bind('<<Drop>>', self.target_img_drag_event)
        self.watermark_drag_zone.drop_target_register(DND_FILES)
        self.watermark_drag_zone.dnd_bind('<<Drop>>', self.watermark_img_drag_event)

    def target_img_drag_event(self, event):

        path = remove_curly_braces(event.data)

        if not is_valid_image(path):
            invalid_messagebox()
            return

        self.target_img_load(path)

    def watermark_img_drag_event(self, event):

        path = remove_curly_braces(event.data)

        if not is_valid_image(path):
            invalid_messagebox()
            return

        self.watermark_img_load(path)

    def destiny_folder_browse_event(self):

        path = filedialog.askdirectory()

        if path is None:
            return

        self.destiny_path.set(path)

    def target_img_browse_event(self):

        path = filedialog.askopenfile()

        if path is None:
            return

        if not is_valid_image(path.name):
            invalid_messagebox()
            return

        self.target_img_load(path.name)

    def watermark_img_browse_event(self):

        path = filedialog.askopenfile()

        if path is None:
            return

        if not is_valid_image(path.name):
            invalid_messagebox()
            return

        self.watermark_img_load(path.name)

    def target_img_load(self, path):

        self.target_image_path.set(path)
        self.target_drag_zone_background = self.get_resized_image(path)
        self.target_drag_zone.configure(image=self.target_drag_zone_background)

    def watermark_img_load(self, path):

        self.watermark_image_path.set(path)
        self.watermark_drag_zone_background = self.get_resized_image(path)
        self.watermark_drag_zone.configure(image=self.watermark_drag_zone_background)

    def generate_preview(self):

        pass

    def get_resized_image(self, path: str) -> ImageTk.PhotoImage:
        resized_image = get_resized_image(Image.open(path), self.img_width, self.img_height)
        return ImageTk.PhotoImage(resized_image)
