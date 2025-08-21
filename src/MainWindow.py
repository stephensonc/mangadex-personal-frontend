import tkinter as tk
from SearchFrame import SearchFrame
from UserInfoFrame import UserInfoFrame
from RequestHandler import RequestHandler
from CredentialManager import CredentialManager

class MainWindow(tk.Tk):
    
    def __init__(self, minsize=(900,950), bg="grey"):
        super(MainWindow, self).__init__()
        # Set background color
        self.config(bg=bg)
        self.title("MangaDex Portal")
        self.minsize(minsize[0], minsize[1])

        self.request_handler = RequestHandler(credential_manager=CredentialManager(file="auth_testing.yml"))
        self.user_info_frame = UserInfoFrame(self.request_handler, self)
        self.search_frame = SearchFrame(self.request_handler, self)
        self.create_menu_bar()

    def create_menu_bar(self):
        self.menu_bar = tk.Menu(self)
        user_menu = tk.Menu(self.menu_bar, tearoff=0)
        user_menu.add_command(label="Refresh follows list", command=self.user_info_frame.create_follows_list_widget)
        user_menu.add_command(label="Logout")
        self.menu_bar.add_cascade(label="Profile", menu=user_menu)
        self.menu_bar.add_command(label="Random Manga", command=self.open_random_manga)
        self.menu_bar.add_cascade(label="Export", )
        self.menu_bar.add_command(label="Exit", command=self.destroy)
        self.config(menu=self.menu_bar)

    def open_random_manga(self):
        pass

def main():
    main_window = MainWindow()
    main_window.mainloop()

if __name__ == "__main__":
    main()