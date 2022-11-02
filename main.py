from tkinterdnd2 import TkinterDnD

from gui import GUI


def main():
    root = TkinterDnD.Tk()
    gui = GUI(root)
    gui.create_widgets()
    gui.register_event_listeners()
    root.mainloop()


if __name__ == '__main__':
    main()
