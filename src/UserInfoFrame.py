import os
import tkinter as tk
from UserProfile import UserProfile

class UserInfoFrame(tk.Frame):

    def __init__(self, master=None):
        super(UserInfoFrame, self).__init__(master)
        self.master = master

        self._username = ""
        self._password = ""
        self.user_profile = self.set_up_user_profile()
        self.pack(side="left")
        self.create_widgets()



    def create_widgets(self):

        self.create_follows_list_widget()
    
    def set_up_user_profile(self):
        user_profile = UserProfile()

        if not user_profile.config_exists():
            # Prompt user for credentials
            self.prompt_for_credentials()
            user_profile.set_user_credentials(self._username, self._password)
        else:
            config_data = user_profile.get_data_from_config()
            user_profile.set_user_credentials(config_data["user_credentials"]["username"], config_data["user_credentials"]["password"])
        
        user_profile.refresh_session()
        return user_profile

    def prompt_for_credentials(self):
       
        window = tk.Toplevel()
        window.title("Login")
        window.minsize(100, 50)
        window.attributes('-topmost', True)
        window.update()

        left_frame = tk.Frame(window)
        left_frame.pack(side="left")

        right_frame = tk.Frame(window)
        right_frame.pack(side="right")


        username_field = tk.Entry(left_frame, width="20")
        username_field.insert(0, "Username")
        username_field.pack(side="top")

        password_field = tk.Entry(left_frame, width="20")
        password_field.insert(0, "Password")
        password_field.pack(side="bottom")

        self._prompt_window = window
        self._username_field = username_field
        self._password_field = password_field
        submit_button = tk.Button(right_frame, text="Submit", command=self.obtain_credentials_from_prompt)
        submit_button.pack(side="right")

        self.wait_window(window)
        return self._password
    
    def obtain_credentials_from_prompt(self):
        self._username = self._username_field.get()
        self._password = self._password_field.get()
        self._prompt_window.destroy()
        
        

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