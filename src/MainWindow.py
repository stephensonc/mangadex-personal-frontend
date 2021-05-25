import tkinter as tk
from UserInfoFrame import UserInfoFrame
from RequestHandler import RequestHandler

class MainWindow(tk.Tk):
    def __init__(self, minsize=(900,950)):
        super(MainWindow, self).__init__()

        self.title("MangaDex Portal")
        self.minsize(minsize[0], minsize[1])

        self._username = ""
        self._password = ""
        self.request_handler = self.set_up_request_handler()

        self.user_info_frame = UserInfoFrame(self.request_handler, self)
        self.create_menu_bar()


    def set_up_request_handler(self):
        request_handler = RequestHandler()

        if not request_handler.config_exists():
            # Prompt user for credentials
            self.prompt_for_credentials()
            request_handler.set_user_credentials(self._username, self._password)
        else:
            config_data = request_handler.get_data_from_config()
            request_handler.set_user_credentials(config_data["user_credentials"]["username"], config_data["user_credentials"]["password"])
        
        request_handler.refresh_session()
        return request_handler

    def prompt_for_credentials(self):
       
       # Create new window
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

        # Required global variables in order to get credentials on button press
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

    def create_menu_bar(self):
        self.menu_bar = tk.Menu(self)
        user_menu = tk.Menu(self.menu_bar, tearoff=0)
        user_menu.add_command(label="Refresh follows list", command=self.user_info_frame.create_follows_list_widget)
        user_menu.add_command(label="Logout")
        self.menu_bar.add_cascade(label="Profile", menu=user_menu)
        self.menu_bar.add_command(label="Exit", command=self.destroy)
        self.config(menu=self.menu_bar)


def main():
    main_window = MainWindow()
    main_window.mainloop()

if __name__ == "__main__":
    main()