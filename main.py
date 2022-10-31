from tkinterdnd2 import TkinterDnD
import tkinter as tk

from gui import GUI


def main():
    root = TkinterDnD.Tk()
    gui = GUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
