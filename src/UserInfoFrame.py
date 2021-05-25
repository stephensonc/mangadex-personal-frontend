import os
from tkinter.constants import END, RAISED
from MangaViewer import MangaViewer
import tkinter as tk

class UserInfoFrame(tk.Frame):

    def __init__(self, request_handler, master=None):
        super(UserInfoFrame, self).__init__(master)

        self.request_handler = request_handler

        self.follows_widget = tk.Listbox(self, width=50, height=40)
        self.followed_manga = self.get_follows_from_profile()

        self.master = master
        self._username = ""
        self._password = ""
        self.pack(side="left")

        self.follows_widget = tk.Listbox(self)
        self.follows_scroll = tk.Scrollbar(self)
        self.submit_box = tk.Button(self)
        self.follows_label = tk.Label(self)
        self.create_follows_list_widget()



    def create_follows_list_widget(self):
        self.follows_widget.destroy()
        self.follows_scroll.destroy()
        self.submit_box.destroy()
        self.follows_label.destroy()
        self.follows_label = tk.Label(self, text=f"{self.request_handler.get_username()}'s followed manga:", relief=RAISED, font=("Arial", 25))
        self.follows_label.pack(side="top")

        self.submit_box = tk.Button(self, text="Open Selected Manga", command=self.open_followed_manga)
        self.submit_box.pack(side="top")

        self.follows_widget = tk.Listbox(self, width=50, height=40)
        
        self.follows_scroll = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.follows_widget.yview)
        self.follows_widget.config(yscrollcommand=self.follows_scroll.set)
        self.follows_scroll.pack(side="right")

        for element in self.followed_manga.keys():
            self.follows_widget.insert(END, element)
        self.follows_widget.pack(side="bottom")
        # self.follows_widget.bind('<<ListboxSelect>>', self.open_followed_manga)

    def open_followed_manga(self, event=None):
        current_selection = self.follows_widget.get(self.follows_widget.curselection())
        manga_id = self.followed_manga[current_selection]["id"]
        # print(f"Opening manga: {current_selection} : {manga_id}")
        manga_viewer = MangaViewer(request_handler=self.request_handler, manga_id=manga_id)


    def get_follows_from_profile(self):
        followed_manga = self.request_handler.get_user_followed_manga_list()
        # for manga in followed_manga:
        #     print(followed_manga[manga]["id"])
        return followed_manga