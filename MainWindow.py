from tkinter import *

class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()

        self.title("MangaDex Portal")
        self.minsize(500,400)


def main():
    main_window = Root()
    main_window.mainloop()

if __name__ == "__main__":
    main()