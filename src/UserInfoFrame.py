import tkinter as tk
from UserProfile import UserProfile

class UserInfoFrame(tk.Frame):

    def __init__(self, master=None, username="", password=""):
        super(UserInfoFrame, self).__init__(master)
        self.master = master
        self.pack(side="left")
        self.user_profile = UserProfile(username, password)
        self.create_widgets()

    def create_widgets(self):

        self.create_follows_list_widget()

        self.button1 = tk.Button(self)
        self.button1["text"] = "This is a button"
        self.button1["command"] = self.say_hello
        self.button1.pack(side="right")
    
    def create_follows_list_widget(self):
        self.follows_label = tk.Label(self, text=f"{self.user_profile.get_username()}'s followed manga:")
        self.follows_label.pack(side="top")
        self.follows_widget = tk.Listbox(self,xscrollcommand=True, yscrollcommand=True, width=50, height=40)
        idx = 0
        for element in self.get_follows_from_profile():
            self.follows_widget.insert(idx, element)
            idx += 1
        self.follows_widget.pack(side="bottom")

    def get_follows_from_profile(self):
        self.user_profile.get_user_followed_manga_list()
        followed_titles = [manga[0] for manga in self.user_profile.followed_titles]
        return followed_titles
    
    def say_hello(self):
        print("Hello, World!")