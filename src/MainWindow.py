import tkinter as tk
from UserInfoFrame import UserInfoFrame

class MainWindow(tk.Tk):
    def __init__(self, minsize=(900,950)):
        super(MainWindow, self).__init__()
        self.title("MangaDex Portal")
        self.minsize(minsize[0], minsize[1])
        self.user_info_frame = self.create_user_frame()
        self.create_menu_bar()

    def create_menu_bar(self):
        self.menu_bar = tk.Menu(self)
        user_menu = tk.Menu(self.menu_bar, tearoff=0)
        user_menu.add_command(label="Refresh follows list", command=self.user_info_frame.create_follows_list_widget)
        self.menu_bar.add_cascade(label="Profile", menu=user_menu)
        self.menu_bar.add_command(label="Exit", command=self.destroy)
        self.config(menu=self.menu_bar)

    def create_user_frame(self, username="", password=""):
        return UserInfoFrame(self, username, password)

    def user_command(self):
        print("Hello World")

def main():
    main_window = MainWindow()
    main_window.mainloop()

if __name__ == "__main__":
    main()