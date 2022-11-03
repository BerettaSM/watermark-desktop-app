import io
import os
import tkinter as tk
from tkinter import N, W, S, E, HORIZONTAL
from tkinter import filedialog
from tkinter import ttk

from PIL import ImageTk, Image
from tkinterdnd2 import DND_FILES, TkinterDnD

from image_processing import IMG_WIDTH, IMG_HEIGHT
from image_processing import get_resized_image, get_resized_photo_image, generate_watermarked_image, Position
from image_processing import is_valid_image, folder_contains_images
from images import IMAGE_BG, IMAGE_FG, WATERMARK_ICON, TRANSPARENT
from utils import get_user_desktop, remove_curly_braces
from utils import invalid_image_messagebox, invalid_dir_messagebox, processed_images_messagebox, about_messagebox

FONT = 'Playball'
TITLE_FONT = (FONT, 24)
SECONDARY_FONT = (FONT, 14)
OPTION_FONT = (FONT, 12)
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

        self.style = None

        self.loading_bar = None
        self.batch_mode = None

        self.destiny_path = None
        self.target_path = None
        self.watermark_image_path = None

        self.target_image_entry = None
        self.watermark_image_entry = None

        self.destiny_button = None
        self.target_image_button = None
        self.watermark_image_button = None

        self.target_title_label = None
        self.watermark_title_label = None
        self.preview_title_label = None

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

        self.options_panel = None

        self.position_label = None
        self.top_left_rd_button = None
        self.top_right_rd_button = None
        self.center_rd_button = None
        self.bot_left_rd_button = None
        self.bot_right_rd_button = None

        self.end_result = None
        self.wm_position = None

        self.should_miniaturize = None
        self.miniature_check = None
        self.save_button = None

    def create_widgets(self):

        my_menu = tk.Menu(self.master)
        self.master.config(menu=my_menu)
        self.master.option_add('*tearOff', False)
        file_menu = tk.Menu(my_menu)
        my_menu.add_cascade(label='File', menu=file_menu)
        help_menu = tk.Menu(my_menu)
        my_menu.add_cascade(label='Help', menu=help_menu)
        file_menu.add_command(label='Quit', command=self.master.quit)
        help_menu.add_command(label='About', command=about_messagebox)

        self.loading_bar = ttk.Progressbar(self, orient=HORIZONTAL, length=200, mode='determinate')
        self.loading_bar.grid(row=0, column=0, columnspan=10, sticky=N + E + S + W, padx=4, ipady=5)
        self.loading_bar.grid_remove()
        self.batch_mode = tk.BooleanVar(value=False)
        batch_mode_check = ttk.Checkbutton(self, text='Batch mode', variable=self.batch_mode,
                                           onvalue=True, offvalue=False, style='TCheckbutton')
        batch_mode_check.grid(row=0, column=10, sticky=E, padx=4, ipady=5)

        self.destiny_button = ttk.Button(self, text='Choose destiny', style='TButton',
                                         command=self.destiny_folder_browse_event, width=20)
        self.destiny_button.grid(row=1, column=0, sticky=W + E, padx=5, pady=5)

        self.destiny_path = tk.StringVar(value=get_user_desktop())
        destiny_entry = ttk.Entry(self, textvariable=self.destiny_path, state='readonly', takefocus=0, width=55)
        destiny_entry.grid(row=1, column=1, columnspan=10, sticky=N + W + S + E, padx=5, pady=5)

        self.target_image_button = ttk.Button(self, text='Choose target image', style='TButton',
                                              command=self.target_browse_event)
        self.target_image_button.grid(row=2, column=0, sticky=W + E, padx=5, pady=5)

        self.target_path = tk.StringVar(value='Choose a target image')
        self.target_image_entry = ttk.Entry(self, textvariable=self.target_path, state='readonly', takefocus=0)
        self.target_image_entry.grid(row=2, column=1, columnspan=10, sticky=N + W + S + E, padx=5, pady=5)

        self.watermark_image_button = ttk.Button(self, text='Choose watermark', style='TButton',
                                                 command=self.watermark_img_browse_event)
        self.watermark_image_button.grid(row=3, column=0, sticky=W + E, padx=5, pady=5)

        self.watermark_image_path = tk.StringVar(value='Choose a watermark image')
        self.watermark_image_entry = ttk.Entry(self, textvariable=self.watermark_image_path,
                                               state='readonly', takefocus=0)
        self.watermark_image_entry.grid(row=3, column=1, columnspan=10, sticky=N + W + S + E, padx=5, pady=5)

        self.target_title_label = ttk.Label(self, text='Target Image',
                                            font=TITLE_FONT, background=LIGHT_BLUE, foreground=DARK_BLUE)
        self.target_title_label.grid(row=4, column=0, columnspan=5, pady=15)

        self.watermark_title_label = ttk.Label(self, text='Your Watermark',
                                               font=TITLE_FONT, background=LIGHT_BLUE, foreground=DARK_BLUE)
        self.watermark_title_label.grid(row=4, column=6, columnspan=5, pady=15)

        self.preview_title_label = ttk.Label(self, text='Preview',
                                             font=TITLE_FONT, background=LIGHT_BLUE, foreground=DARK_BLUE)
        self.preview_title_label.grid(row=11, column=0, columnspan=5, pady=15)

        self.target_drag_zone_wrapper_image = ImageTk.PhotoImage(Image.open(io.BytesIO(IMAGE_BG)))
        self.target_drag_zone_wrapper = tk.Label(self, image=self.target_drag_zone_wrapper_image)
        self.target_drag_zone_wrapper.configure(width=270, height=170)
        self.target_drag_zone_wrapper.grid(row=5, column=0, columnspan=5, rowspan=5, padx=7)

        self.target_drag_zone_background = get_resized_photo_image(bytes_=IMAGE_FG)
        self.target_drag_zone = tk.Label(self.target_drag_zone_wrapper, image=self.target_drag_zone_background)
        self.target_drag_zone.configure(width=IMG_WIDTH, height=IMG_HEIGHT, background=LIGHT_BLUE)
        self.target_drag_zone.grid(row=0, column=0, pady=7, padx=7)

        self.watermark_drag_zone_wrapper_image = ImageTk.PhotoImage(Image.open(io.BytesIO(IMAGE_BG)))
        self.watermark_drag_zone_wrapper = tk.Label(self, image=self.target_drag_zone_wrapper_image)
        self.watermark_drag_zone_wrapper.configure(width=270, height=170)
        self.watermark_drag_zone_wrapper.grid(row=5, column=6, columnspan=5, rowspan=5, padx=7)

        self.watermark_drag_zone_background = get_resized_photo_image(bytes_=IMAGE_FG)
        self.watermark_drag_zone = tk.Label(self.watermark_drag_zone_wrapper, image=self.watermark_drag_zone_background)
        self.watermark_drag_zone.configure(width=IMG_WIDTH, height=IMG_HEIGHT, background=LIGHT_BLUE)
        self.watermark_drag_zone.grid(row=0, column=0, pady=7, padx=7)

        self.preview_zone_wrapper_image = ImageTk.PhotoImage(Image.open(io.BytesIO(IMAGE_BG)))
        self.preview_zone_wrapper = tk.Label(self, image=self.preview_zone_wrapper_image)
        self.preview_zone_wrapper.configure(width=270, height=170)
        self.preview_zone_wrapper.grid(row=12, column=0, columnspan=5, rowspan=5, padx=7)

        self.preview_zone_background = get_resized_photo_image(bytes_=TRANSPARENT)
        self.preview_zone = tk.Label(self.preview_zone_wrapper, image=self.preview_zone_background)
        self.preview_zone.configure(width=IMG_WIDTH, height=IMG_HEIGHT, background=LIGHT_BLUE)
        self.preview_zone.grid(row=0, column=0, pady=7, padx=7)

        self.position_label = ttk.Label(self, text='Choose position',
                                        font=TITLE_FONT, background=LIGHT_BLUE, foreground=DARK_BLUE)
        self.position_label.grid(row=11, column=6, columnspan=5)

        self.options_panel = ttk.Frame(self)
        self.options_panel.grid(row=12, column=6, columnspan=5, rowspan=5, sticky=N + W + E + S, padx=7)
        self.options_panel.grid_rowconfigure(0, weight=1)

        self.wm_position = tk.StringVar(value=Position.BOTTOM_RIGHT.value)
        self.top_left_rd_button = ttk.Radiobutton(self.options_panel, text=Position.TOP_LEFT.value,
                                                  variable=self.wm_position, value=Position.TOP_LEFT.value,
                                                  style='TRadiobutton')
        self.top_right_rd_button = ttk.Radiobutton(self.options_panel, text=Position.TOP_RIGHT.value,
                                                   variable=self.wm_position, value=Position.TOP_RIGHT.value,
                                                   style='TRadiobutton')
        self.center_rd_button = ttk.Radiobutton(self.options_panel, text=Position.CENTER.value,
                                                variable=self.wm_position, value=Position.CENTER.value,
                                                style='TRadiobutton')
        self.bot_left_rd_button = ttk.Radiobutton(self.options_panel, text=Position.BOTTOM_LEFT.value,
                                                  variable=self.wm_position, value=Position.BOTTOM_LEFT.value,
                                                  style='TRadiobutton')
        self.bot_right_rd_button = ttk.Radiobutton(self.options_panel, text=Position.BOTTOM_RIGHT.value,
                                                   variable=self.wm_position, value=Position.BOTTOM_RIGHT.value,
                                                   style='TRadiobutton')

        self.top_left_rd_button.grid(row=0, column=0, sticky=N+W)
        self.bot_left_rd_button.grid(row=1, column=0,  sticky=N+W)
        self.center_rd_button.grid(row=0, column=2, sticky=S)
        self.top_right_rd_button.grid(row=0, column=4, sticky=N+E)
        self.bot_right_rd_button.grid(row=1, column=4, sticky=N+E)

        self.should_miniaturize = tk.BooleanVar(value=False)
        self.miniature_check = ttk.Checkbutton(self.options_panel, text='Miniaturize watermark',
                                               onvalue=True, offvalue=False,
                                               variable=self.should_miniaturize, style='TCheckbutton')
        self.miniature_check.grid(row=3, column=0, columnspan=5, ipady=20)

        self.save_button = ttk.Button(self.options_panel, text='No valid images selected', style='TButton',
                                      command=self.save_single_image_event, width=21)
        self.save_button.grid(row=4, column=0, columnspan=5, sticky=W+E+S)
        self.save_button.state(['disabled'])

        self.set_up_styling()

    def register_event_listeners(self):

        self.target_drag_zone.drop_target_register(DND_FILES)
        self.target_drag_zone.dnd_bind('<<Drop>>', self.target_drag_event)
        self.watermark_drag_zone.drop_target_register(DND_FILES)
        self.watermark_drag_zone.dnd_bind('<<Drop>>', self.watermark_img_drag_event)

        self.target_image_entry.drop_target_register(DND_FILES)
        self.target_image_entry.dnd_bind('<<Drop>>', self.target_drag_event)
        self.watermark_image_entry.drop_target_register(DND_FILES)
        self.watermark_image_entry.dnd_bind('<<Drop>>', self.watermark_img_drag_event)

        self.wm_position.trace('w', self.validate_state)
        self.should_miniaturize.trace('w', self.validate_state)

        self.batch_mode.trace('w', self.switch_batch_mode_layout)

    def target_drag_event(self, event):

        path = remove_curly_braces(event.data)

        batch = self.batch_mode.get()

        if batch:

            if not os.path.isdir(path):
                invalid_dir_messagebox()
                return

            self.target_path.set(path)

            self.validate_paths()

        else:

            if not is_valid_image(path):
                invalid_image_messagebox()
                return

            self.target_file_load(path)

    def watermark_img_drag_event(self, event):

        path = remove_curly_braces(event.data)

        if not is_valid_image(path):
            invalid_image_messagebox()
            return

        self.watermark_img_load(path)

    def destiny_folder_browse_event(self):

        path = filedialog.askdirectory()

        if not path:
            return

        self.destiny_path.set(path)

    def target_browse_event(self):

        batch = self.batch_mode.get()

        if batch:
            path = filedialog.askdirectory()

            if not path:
                return

            self.target_path.set(path)

            self.validate_state()

        else:
            path = filedialog.askopenfile()

            if not path:
                return

            if not is_valid_image(path.name):
                invalid_image_messagebox()
                return

            self.target_file_load(path.name)

    def watermark_img_browse_event(self):

        path = filedialog.askopenfile()

        if path is None:
            return

        if not is_valid_image(path.name):
            invalid_image_messagebox()
            return

        self.watermark_img_load(path.name)

    def target_file_load(self, path):

        self.target_path.set(path)
        self.target_drag_zone_background = get_resized_photo_image(path)
        self.target_drag_zone.configure(image=self.target_drag_zone_background)

        self.validate_state()

    def watermark_img_load(self, path):

        self.watermark_image_path.set(path)
        self.watermark_drag_zone_background = get_resized_photo_image(path)
        self.watermark_drag_zone.configure(image=self.watermark_drag_zone_background)

        self.validate_state()

    def validate_state(self, *args):

        paths_are_valid = self.validate_paths()
        batch = self.batch_mode.get()

        if paths_are_valid:

            if not batch:
                self.generate_single_image()

    def generate_single_image(self):

        target_image = Image.open(self.target_path.get())
        watermark_image = Image.open(self.watermark_image_path.get())
        position = self.wm_position.get()
        should_miniaturize = self.should_miniaturize.get()

        self.end_result = generate_watermarked_image(target_image, watermark_image,
                                                     position, should_miniaturize)

        self.preview_img_load()

    def preview_img_load(self):

        resized_image = get_resized_image(self.end_result)
        self.preview_zone_background = ImageTk.PhotoImage(resized_image)
        self.preview_zone.configure(image=self.preview_zone_background)

    def save_single_image_event(self):

        dest = self.destiny_path.get()
        filepath = self.target_path.get()

        filename = os.path.basename(filepath)
        new_filename = 'watermarked_' + filename

        new_file_path = os.path.join(dest, new_filename)
        self.end_result.save(new_file_path)

    def validate_paths(self):

        target = self.target_path.get()
        watermark = self.watermark_image_path.get()

        batch = self.batch_mode.get()

        is_valid_watermark = is_valid_image(watermark)

        if batch:
            is_valid_target = folder_contains_images(target)

        else:
            is_valid_target = is_valid_image(target)

        both_paths_set = is_valid_watermark and is_valid_target

        if both_paths_set:
            self.save_button.state(['!disabled'])

            if batch:
                updated_button_inner_text = 'Generate/save batch'

            else:
                updated_button_inner_text = 'Save image'

        else:
            self.save_button.state(['disabled'])

            if batch:
                if is_valid_watermark:
                    updated_button_inner_text = 'No valid images inside target folder'

                else:
                    updated_button_inner_text = 'No watermark selected'

            else:
                updated_button_inner_text = 'No valid images selected'

        self.save_button.configure(text=updated_button_inner_text)

        return both_paths_set

    def generate_and_save_batch_event(self):

        # Disable buttons
        self.destiny_button.state(['disabled'])
        self.target_image_button.state(['disabled'])
        self.watermark_image_button.state(['disabled'])
        self.save_button.state(['disabled'])

        self.save_button.configure(text='In progress...')

        # Enable loading bar
        self.loading_bar.grid()

        target_folder = self.target_path.get()
        dump_folder = os.path.join(self.destiny_path.get(), 'watermarked images')

        watermark_image = Image.open(self.watermark_image_path.get())
        position = self.wm_position.get()
        should_miniaturize = self.should_miniaturize.get()

        if not os.path.isdir(dump_folder):
            os.makedirs(dump_folder)

        loading_bar_increment = 100 / len(os.listdir(target_folder))

        processed_images = 0

        for file in os.listdir(target_folder):

            self.loading_bar['value'] += loading_bar_increment

            self.save_button.configure(text=f'In progress: {self.loading_bar.cget("value"):.1f}%')

            # Force update gui widgets
            self.master.update_idletasks()

            full_file_path = os.path.join(target_folder, file)

            if not is_valid_image(full_file_path):
                continue

            target_image = Image.open(full_file_path)

            watermarked_image = generate_watermarked_image(target_image, watermark_image,
                                                           position, should_miniaturize)

            filename = os.path.basename(full_file_path)
            new_filename = 'watermarked_' + filename

            new_file_path = os.path.join(dump_folder, new_filename)

            watermarked_image.save(new_file_path)

            processed_images += 1

        # Reset progress bar
        self.loading_bar.stop()

        # Re-enable buttons
        self.destiny_button.state(['!disabled'])
        self.target_image_button.state(['!disabled'])
        self.watermark_image_button.state(['!disabled'])
        self.save_button.state(['!disabled'])

        self.save_button.configure(text='Generate/save batch')

        # Hide loading bar
        self.loading_bar.grid_remove()

        processed_images_messagebox(processed_images)

    def switch_batch_mode_layout(self, *args):

        self.validate_paths()

        batch = self.batch_mode.get()

        if batch:
            # Batch layout
            self.target_image_button.configure(text='Choose target folder')
            self.target_path.set(value='Choose a folder, all images inside will be watermarked')

            self.target_title_label.grid_remove()
            self.preview_title_label.grid_remove()

            self.target_drag_zone_wrapper.grid_remove()
            self.target_drag_zone.grid_remove()

            self.preview_zone_wrapper.grid_remove()
            self.preview_zone.grid_remove()

            self.watermark_title_label.grid(row=4, column=0)
            self.watermark_drag_zone_wrapper.grid(row=5, column=0)

            self.position_label.grid(row=4, column=6)
            self.options_panel.grid(row=5, column=6)
            self.save_button.configure(command=self.generate_and_save_batch_event)

        else:
            # Normal layout
            self.target_image_button.configure(text='Choose target image')
            self.target_path.set(value='Choose a target image')

            self.target_title_label.grid()
            self.preview_title_label.grid()

            self.target_drag_zone_wrapper.grid()
            self.target_drag_zone.grid()
            self.target_drag_zone_background = get_resized_photo_image(bytes_=IMAGE_FG)
            self.target_drag_zone.configure(image=self.target_drag_zone_background)

            self.preview_zone_wrapper.grid()
            self.preview_zone.grid()
            self.preview_zone_background = get_resized_photo_image(bytes_=TRANSPARENT)
            self.preview_zone.configure(image=self.preview_zone_background)

            self.watermark_title_label.grid(row=4, column=6)
            self.watermark_drag_zone_wrapper.grid(row=5, column=6)

            self.position_label.grid(row=11, column=6)
            self.options_panel.grid(row=12, column=6)
            self.save_button.configure(command=self.save_single_image_event)

    def switch_buttons_state(self):

        is_save_button_enabled = self.save_button.instate(['!disabled'])

        if is_save_button_enabled:
            self.destiny_button.state(['!disabled'])
            self.target_image_button.state(['!disabled'])
            self.watermark_image_button.state(['!disabled'])
            self.save_button.state(['!disabled'])

        else:
            self.destiny_button.state(['disabled'])
            self.target_image_button.state(['disabled'])
            self.watermark_image_button.state(['disabled'])
            self.save_button.state(['disabled'])

    def set_up_styling(self):

        self.style = ttk.Style()

        self.style.theme_use('clam')
        self.style.configure('TFrame', background=LIGHT_BLUE)
        self.style.configure('Horizontal.TProgressbar', background=MAIN_BLUE, darkcolor=DARK_BLUE,
                             bordercolor=LIGHT_BLUE, lightcolor=LIGHTER_BLUE)
        self.style.configure('TEntry', foreground=DARK_BLUE, font=SECONDARY_FONT)
        self.style.configure('TButton', borderwith=2, font=SECONDARY_FONT, width=10)
        self.style.configure('TRadiobutton', font=OPTION_FONT)
        self.style.configure('TCheckbutton', font=OPTION_FONT)
        self.style.map('TButton',
                       foreground=[('disabled', 'gray'), ('!active', DARK_BLUE),
                                   ('pressed', LIGHT_BLUE), ('active', MAIN_BLUE)],
                       background=[('disabled', LIGHTER_BLUE), ('!active', LIGHT_BLUE),
                                   ('pressed', DARK_BLUE), ('active', LIGHT_BLUE)]
                       )
        self.style.map('TRadiobutton',
                       foreground=[('!active', DARK_BLUE), ('pressed', MAIN_BLUE), ('active', MAIN_BLUE)],
                       background=[('!active', LIGHT_BLUE), ('pressed', LIGHT_BLUE), ('active', LIGHT_BLUE)]
                       )
        self.style.map('TCheckbutton',
                       foreground=[('!active', DARK_BLUE), ('pressed', MAIN_BLUE), ('active', MAIN_BLUE)],
                       background=[('!active', LIGHT_BLUE), ('pressed', LIGHT_BLUE), ('active', LIGHT_BLUE)]
                       )
