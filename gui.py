import io
import os
import tkinter as tk
from tkinter import N, W, S, E
from tkinter import filedialog
from tkinter import ttk

from PIL import ImageTk, Image
from tkinterdnd2 import DND_FILES, TkinterDnD

from image_processing import IMG_WIDTH, IMG_HEIGHT
from image_processing import get_resized_image, is_valid_image, generate_watermarked_image, Position
from images import IMAGE_BG, IMAGE_FG, WATERMARK_ICON, TRANSPARENT
from utils import get_user_desktop, remove_curly_braces, invalid_messagebox

FONT = 'Playball'
TITLE_FONT = (FONT, 24)
SECONDARY_FONT = (FONT, 14)
LIGHTER_BLUE = '#E1F0FA'
LIGHT_BLUE = '#D0EAFB'
MAIN_BLUE = '#1077BC'
DARK_BLUE = '#083C5E'


class GUI(ttk.Frame):

    def __init__(self, master: TkinterDnD.Tk):

        super().__init__(master=master)

        self.master: TkinterDnD.Tk = master
        self.master.title("Watermark Desktop App")
        ico = ImageTk.PhotoImage(Image.open(io.BytesIO(WATERMARK_ICON)))
        self.master.wm_iconphoto(False, ico)
        self.master.resizable(width=False, height=False)

        self.grid(row=0, column=0)
        self.configure(padding="40")

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

        self.end_result_image = None
        self.wm_position = None

        self.should_miniaturize = None
        self.save_button = None

        self.create_widgets()
        self.register_event_listeners()

    def create_widgets(self):

        s = ttk.Style()
        s.theme_use('clam')
        s.configure('TFrame', background=LIGHT_BLUE)
        s.configure('TEntry', foreground=DARK_BLUE, font=SECONDARY_FONT)
        s.configure('TButton', borderwith=2, font=SECONDARY_FONT)
        s.map('C.TButton',
              foreground=[('disabled', 'light gray'), ('!active', DARK_BLUE),
                          ('pressed', LIGHT_BLUE), ('active', MAIN_BLUE)],
              background=[('disabled', LIGHTER_BLUE), ('!active', LIGHT_BLUE),
                          ('pressed', DARK_BLUE), ('active', LIGHT_BLUE)]
              )
        s.map("C.TRadiobutton",
              foreground=[('!active', DARK_BLUE), ('pressed', MAIN_BLUE), ('active', MAIN_BLUE)],
              background=[('!active', LIGHT_BLUE), ('pressed', LIGHT_BLUE), ('active', LIGHT_BLUE)]
              )
        s.map("C.TCheckbutton",
              foreground=[('!active', DARK_BLUE), ('pressed', MAIN_BLUE), ('active', MAIN_BLUE)],
              background=[('!active', LIGHT_BLUE), ('pressed', LIGHT_BLUE), ('active', LIGHT_BLUE)]
              )

        destiny_button = ttk.Button(self, text='Choose destiny', style='C.TButton',
                                    command=self.destiny_folder_browse_event)
        destiny_button.grid(row=0, column=0, sticky=W + E, padx=5, pady=5)

        self.destiny_path = tk.StringVar(value=get_user_desktop())
        destiny_entry = ttk.Entry(self, textvariable=self.destiny_path, state='readonly', takefocus=0)
        destiny_entry.grid(row=0, column=1, columnspan=10, sticky=N + W + S + E, padx=5, pady=5)

        target_image_button = ttk.Button(self, text='Choose target', style='C.TButton',
                                         command=self.target_img_browse_event)
        target_image_button.grid(row=1, column=0, sticky=W + E, padx=5, pady=5)

        self.target_image_path = tk.StringVar(value='Choose a target image')
        target_image_entry = ttk.Entry(self, textvariable=self.target_image_path, state='readonly', takefocus=0)
        target_image_entry.grid(row=1, column=1, columnspan=10, sticky=N + W + S + E, padx=5, pady=5)

        watermark_image_button = ttk.Button(self, text='Choose watermark', style='C.TButton',
                                            command=self.watermark_img_browse_event)
        watermark_image_button.grid(row=2, column=0, sticky=W + E, padx=5, pady=5)

        self.watermark_image_path = tk.StringVar(value='Choose a watermark image')
        watermark_image_entry = ttk.Entry(self, textvariable=self.watermark_image_path, state='readonly', takefocus=0)
        watermark_image_entry.grid(row=2, column=1, columnspan=10, sticky=N + W + S + E, padx=5, pady=5)

        target_title_label = ttk.Label(self, text='Target Image',
                                       font=TITLE_FONT, background=LIGHT_BLUE, foreground=DARK_BLUE)
        target_title_label.grid(row=3, column=0, columnspan=5, pady=15)

        watermark_title_label = ttk.Label(self, text='Your Watermark',
                                          font=TITLE_FONT, background=LIGHT_BLUE, foreground=DARK_BLUE)
        watermark_title_label.grid(row=3, column=5, columnspan=5, pady=15)

        preview_title_label = ttk.Label(self, text='Preview',
                                        font=TITLE_FONT, background=LIGHT_BLUE, foreground=DARK_BLUE)
        preview_title_label.grid(row=5, column=0, columnspan=5, pady=15)

        self.target_drag_zone_wrapper_image = ImageTk.PhotoImage(Image.open(io.BytesIO(IMAGE_BG)))
        self.target_drag_zone_wrapper = tk.Label(self, image=self.target_drag_zone_wrapper_image)
        self.target_drag_zone_wrapper.configure(width=270, height=170)
        self.target_drag_zone_wrapper.grid(row=4, column=0, columnspan=5, padx=7)

        self.target_drag_zone_background = self.get_resized_image(bytes_=IMAGE_FG)
        self.target_drag_zone = tk.Label(self.target_drag_zone_wrapper, image=self.target_drag_zone_background)
        self.target_drag_zone.configure(width=IMG_WIDTH, height=IMG_HEIGHT, background=LIGHT_BLUE)
        self.target_drag_zone.grid(row=0, column=0, pady=7, padx=7)

        self.watermark_drag_zone_wrapper_image = ImageTk.PhotoImage(Image.open(io.BytesIO(IMAGE_BG)))
        self.watermark_drag_zone_wrapper = tk.Label(self, image=self.target_drag_zone_wrapper_image)
        self.watermark_drag_zone_wrapper.configure(width=270, height=170)
        self.watermark_drag_zone_wrapper.grid(row=4, column=6, columnspan=5, padx=7)

        self.watermark_drag_zone_background = self.get_resized_image(bytes_=IMAGE_FG)
        self.watermark_drag_zone = tk.Label(self.watermark_drag_zone_wrapper, image=self.watermark_drag_zone_background)
        self.watermark_drag_zone.configure(width=IMG_WIDTH, height=IMG_HEIGHT, background=LIGHT_BLUE)
        self.watermark_drag_zone.grid(row=0, column=0, pady=7, padx=7)

        self.preview_zone_wrapper_image = ImageTk.PhotoImage(Image.open(io.BytesIO(IMAGE_BG)))
        self.preview_zone_wrapper = tk.Label(self, image=self.preview_zone_wrapper_image)
        self.preview_zone_wrapper.configure(width=270, height=170)
        self.preview_zone_wrapper.grid(row=6, column=0, columnspan=5, rowspan=5, padx=7)

        self.preview_zone_background = self.get_resized_image(bytes_=TRANSPARENT)
        self.preview_zone = tk.Label(self.preview_zone_wrapper, image=self.preview_zone_background)
        self.preview_zone.configure(width=IMG_WIDTH, height=IMG_HEIGHT, background=LIGHT_BLUE)
        self.preview_zone.grid(row=0, column=0, pady=7, padx=7)

        position_label = ttk.Label(self, text='Choose position',
                                   font=SECONDARY_FONT, background=LIGHT_BLUE, foreground=DARK_BLUE)
        position_label.grid(row=5, column=6, columnspan=5)

        self.wm_position = tk.StringVar(value=Position.BOTTOM_RIGHT.value)
        top_left_rd_button = ttk.Radiobutton(self, text=Position.TOP_LEFT.value, variable=self.wm_position,
                                             value=Position.TOP_LEFT.value, style='C.TRadiobutton')
        top_right_rd_button = ttk.Radiobutton(self, text=Position.TOP_RIGHT.value, variable=self.wm_position,
                                              value=Position.TOP_RIGHT.value, style='C.TRadiobutton')
        center_rd_button = ttk.Radiobutton(self, text=Position.CENTER.value, variable=self.wm_position,
                                           value=Position.CENTER.value, style='C.TRadiobutton')
        bot_left_rd_button = ttk.Radiobutton(self, text=Position.BOTTOM_LEFT.value, variable=self.wm_position,
                                             value=Position.BOTTOM_LEFT.value, style='C.TRadiobutton')
        bot_right_rd_button = ttk.Radiobutton(self, text=Position.BOTTOM_RIGHT.value, variable=self.wm_position,
                                              value=Position.BOTTOM_RIGHT.value, style='C.TRadiobutton')

        top_left_rd_button.grid(row=6, column=6, sticky=W)
        bot_left_rd_button.grid(row=7, column=6, columnspan=2, sticky=W)
        center_rd_button.grid(row=6, column=7)
        top_right_rd_button.grid(row=6, column=8, sticky=E)
        bot_right_rd_button.grid(row=7, column=8, sticky=E)

        self.should_miniaturize = tk.BooleanVar(value=False)
        miniature_check = ttk.Checkbutton(self, text='Miniaturize watermark', variable=self.should_miniaturize,
                                          onvalue=True, offvalue=False, style='C.TCheckbutton')
        miniature_check.grid(row=9, column=6, columnspan=5)

        self.save_button = ttk.Button(self, text='Save image', style='C.TButton',
                                      command=self.save_end_result)
        self.save_button.grid(row=10, column=6, columnspan=5, sticky=W + E)
        self.save_button.state(['disabled'])

    def register_event_listeners(self):

        self.target_drag_zone.drop_target_register(DND_FILES)
        self.target_drag_zone.dnd_bind('<<Drop>>', self.target_img_drag_event)
        self.watermark_drag_zone.drop_target_register(DND_FILES)
        self.watermark_drag_zone.dnd_bind('<<Drop>>', self.watermark_img_drag_event)

        self.wm_position.trace('w', self.update_end_result)
        self.should_miniaturize.trace('w', self.update_end_result)

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

        if not path:
            return

        self.destiny_path.set(path)

    def target_img_browse_event(self):

        path = filedialog.askopenfile()

        if not path:
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

        self.update_end_result()

    def watermark_img_load(self, path):

        self.watermark_image_path.set(path)
        self.watermark_drag_zone_background = self.get_resized_image(path)
        self.watermark_drag_zone.configure(image=self.watermark_drag_zone_background)

        self.update_end_result()

    def preview_img_load(self):

        resized_image = get_resized_image(self.end_result_image)
        self.preview_zone_background = ImageTk.PhotoImage(resized_image)
        self.preview_zone.configure(image=self.preview_zone_background)

    def generate_end_result(self):

        target_image = Image.open(self.target_image_path.get())
        watermark_image = Image.open(self.watermark_image_path.get())
        position = self.wm_position.get()

        self.end_result_image = generate_watermarked_image(target_image, watermark_image,
                                                           position, self.should_miniaturize.get())

        self.preview_img_load()

    def update_end_result(self, *args):

        if self.are_valid_paths_set():
            self.generate_end_result()

    @staticmethod
    def get_resized_image(path: str = None, bytes_: bytes = None) -> ImageTk.PhotoImage:

        if path is None and bytes_ is None:
            raise ValueError('path or bytes_must be provided')

        if path:
            # Reading an image from a path string
            resized_image = get_resized_image(Image.open(path))

        else:
            # Reading an image from images.py, which is set in bytes
            resized_image = get_resized_image(Image.open(io.BytesIO(bytes_)))

        return ImageTk.PhotoImage(resized_image)

    def save_end_result(self):

        dest = self.destiny_path.get()
        filepath = self.target_image_path.get()

        filename = os.path.basename(filepath)
        new_filename = 'watermarked_' + filename

        new_file_path = os.path.join(dest, new_filename)
        self.end_result_image.save(new_file_path)

    def are_valid_paths_set(self):

        target = self.target_image_path.get()
        watermark = self.watermark_image_path.get()

        both_paths_set = is_valid_image(target) and is_valid_image(watermark)

        if both_paths_set:
            self.save_button.state(['!disabled'])

        else:
            self.save_button.state(['disabled'])

        return both_paths_set
