import tkinter as tk
from SearchFrame import SearchFrame
from UserInfoFrame import UserInfoFrame
from RequestHandler import RequestHandler
from CredentialManager import CredentialManager
from DataExporter import DataExporter

class MainWindow(tk.Tk):
    
    def __init__(self, minsize=(900,950), bg="grey"):
        super(MainWindow, self).__init__()
        # Set background color
        self.config(bg=bg)
        self.title("MangaDex Portal")
        self.minsize(minsize[0], minsize[1])
        
        self.request_handler = RequestHandler(credential_manager=CredentialManager())
        self.data_exporter = DataExporter(self.request_handler)

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
        
        self.create_export_menu_option()

        self.menu_bar.add_command(label="Exit", command=self.destroy)
        self.config(menu=self.menu_bar)

    def create_export_menu_option(self):
        export_menu = tk.Menu(self.menu_bar, tearoff=0)
        follows_export_menu = tk.Menu(export_menu, tearoff=0)
        follows_export_menu.add_command(label="List", command=self.data_exporter.export_follows_as_list_ui)
        follows_export_menu.add_command(label="JSON", command=self.data_exporter.export_follows_as_json_ui)
        export_menu.add_cascade(label="Follows List", menu=follows_export_menu)
        self.menu_bar.add_cascade(label="Export", menu=export_menu)


    def open_random_manga(self):
        pass

def main():
    main_window = MainWindow()
    main_window.mainloop()

if __name__ == "__main__":
    main()