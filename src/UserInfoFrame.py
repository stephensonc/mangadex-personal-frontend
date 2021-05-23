import os
import tkinter as tk

class UserInfoFrame(tk.Frame):

    def __init__(self, request_handler, master=None):
        super(UserInfoFrame, self).__init__(master)

        self.request_handler = request_handler


        self.master = master
        self._username = ""
        self._password = ""
        self.pack(side="left")
        self.create_widgets()

    def create_widgets(self):

        self.create_follows_list_widget()

    def create_follows_list_widget(self):
        self.follows_label = tk.Label(self, text=f"{self.request_handler.get_username()}'s followed manga:")
        self.follows_label.pack(side="top")
        self.follows_widget = tk.Listbox(self,xscrollcommand=tk.Scrollbar(), yscrollcommand=tk.Scrollbar(), width=50, height=40)
        idx = 0
        for element in self.get_follows_from_profile():
            self.follows_widget.insert(idx, element)
            idx += 1
        self.follows_widget.pack(side="bottom")

    def get_follows_from_profile(self):
        self.request_handler.get_user_followed_manga_list()
        followed_titles = [manga[0] for manga in self.request_handler.followed_titles]
        return followed_titles