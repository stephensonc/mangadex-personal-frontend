import os
import tkinter as tk

import yaml

class CredentialManager:
    def __init__(self, file="auth_config.yml", username="", password="", client_id="", client_secret=""):
        self._default_auth_config = {
            "user_credentials": {
                "username": "",
                "password": "",
                "client_id": "",
                "client_secret": ""
            },
            "refresh_token": "",
            "access_token": ""
        }
        self._cache_file = file
        self.refresh_token = ""
        self.access_token = ""
        if username=="" or password=="" or client_id=="" or client_secret=="":
            if not self.cache_exists():
                self.prompt_for_credentials()
            self.get_data_from_cache()
        else:
            self.username = username
            self.password = password
            self.client_id = client_id
            self.client_secret = client_secret
            self.cache_credentials()

    def prompt_for_credentials(self, lastFailed=False):
       # Create new window
        window = tk.Toplevel()
        window.title("Login")
        window.minsize(200, 100)
        window.attributes('-topmost', True)
        
        # window.update()

        left_frame = tk.Frame(window)
        left_frame.pack(side="left")
        right_frame = tk.Frame(window)
        right_frame.pack(side="right")

        username_label = tk.Label(left_frame, text="Username: ")
        username_field = tk.Entry(left_frame, width="20")
        username_label.grid(row=0, column=0, sticky='w')
        username_field.grid(row=0, column=1, sticky='w')

        password_field = tk.Entry(left_frame, width="20")
        tk.Label(left_frame, text="Password: ").grid(row=1, column=0,sticky='w')
        password_field.grid(row=1,column=1, sticky='w')

        client_id_field = tk.Entry(left_frame, width="20")
        tk.Label(left_frame, text="Client ID: ").grid(row=2, column=0,sticky='w')
        client_id_field.grid(row=2,column=1, sticky='w')

        client_secret_field = tk.Entry(left_frame, width="20")
        tk.Label(left_frame, text="Client Secret: ").grid(row=3, column=0,sticky='w')
        client_secret_field.grid(row=3,column=1, sticky='w')

        if lastFailed:
            error = tk.Label(right_frame, text="Login Failed!\nPlease try again.", fg="red")
            error.pack(side="top", pady=10)

        # Required global variables in order to get credentials on button press
        self._username_field = username_field
        self._password_field = password_field
        self._client_id_field = client_id_field
        self._client_secret_field = client_secret_field
        submit_button = tk.Button(right_frame, text="Submit", command=self.get_credentials_from_prompt)
        submit_button.pack(side="bottom")
        window.update()
        self._prompt_window = window
        self._prompt_window.wait_window()

    def get_credentials_from_prompt(self):
        self.username = self._username_field.get()
        self.password = self._password_field.get()
        self.client_id = self._client_id_field.get()
        self.client_secret = self._client_secret_field.get()
        self._prompt_window.destroy()
        self.cache_credentials()

    def cache_exists(self):
        file_exists = os.path.isfile(self._cache_file)
        if not file_exists:
            return False
        else:
            config_dict = {}
            with open(self._cache_file) as auth_configfile:
                config_dict = yaml.safe_load(auth_configfile)
                
            # Check if config file expected keys have values. If not, return false
            if len(config_dict) != 0 :
                expected_creds = self._default_auth_config.get("user_credentials").keys()
                actual_file_creds = config_dict.get("user_credentials")
                if actual_file_creds is not None:
                    all_creds_have_values = True
                    for key in expected_creds:
                        file_cred = actual_file_creds.get(key)
                        if file_cred is None or file_cred == "":
                            all_creds_have_values = False
                            break
                    return all_creds_have_values
                else:
                    return False
            else:
                return False

    def get_data_from_cache(self):
        if self.cache_exists():
            with open(self._cache_file) as auth_configfile:
                config_data = yaml.safe_load(auth_configfile)
                self.username = config_data["user_credentials"]["username"]
                self.password = config_data["user_credentials"]["password"]
                self.client_id = config_data["user_credentials"]["client_id"]
                self.client_secret = config_data["user_credentials"]["client_secret"]
                self.access_token = config_data["access_token"]
                self.refresh_token = config_data["refresh_token"]
                return config_data
        else:
            return {}

    def cache_credentials(self):
        yaml_dict = self.get_data_from_cache() if self.cache_exists() else self._default_auth_config
        yaml_dict["user_credentials"]["username"] = self.username
        yaml_dict["user_credentials"]["password"] = self.password
        yaml_dict["user_credentials"]["client_id"] = self.client_id
        yaml_dict["user_credentials"]["client_secret"] = self.client_secret
        yaml_dict["refresh_token"] = self.refresh_token
        yaml_dict["access_token"] = self.access_token
        with open(self._cache_file, "w") as configfile:
            yaml.safe_dump(yaml_dict, configfile)

    def update_tokens_in_cache(self, access_token="", refresh_token=""):
        yaml_dict = self._default_auth_config
        with open(self._cache_file, "r") as auth_configfile:
            yaml_dict = yaml.safe_load(auth_configfile)
            yaml_dict["access_token"] = access_token if access_token!="" else self.access_token
            yaml_dict["refresh_token"] = refresh_token if refresh_token!="" else self.refresh_token
        with open(self._cache_file, "w") as auth_configfile:
            yaml.safe_dump(yaml_dict, auth_configfile)

    def clear_cache(self):
        self.username=""
        self.password=""
        self.client_id=""
        self.client_secret=""
        with open(self._cache_file, "w") as configfile:
            yaml.safe_dump(self._default_auth_config, configfile)