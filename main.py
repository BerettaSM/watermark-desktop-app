from tkinterdnd2 import TkinterDnD

from gui import GUI


def main():
    root = TkinterDnD.Tk()
    GUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
