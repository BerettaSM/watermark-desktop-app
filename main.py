from tkinterdnd2 import TkinterDnD

from gui import GUI


def main():
    root = TkinterDnD.Tk()
    GUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

# pyinstaller.exe --onefile --icon=drop.ico --collect-all tkinterdnd2 main.pyw
# compile with pyinstaller
