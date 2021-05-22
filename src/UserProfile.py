from requests.models import Response
import os
import yaml
import requests


class UserProfile:
    """Facilitate iteractions with user-specific data."""

    def __init__(self, username="", password="") -> None:

        self._default_auth_config = {
            "user_credentials": {"username": username, "password": password},
            "refresh_token": ""
        }
        if username == "" or password == "":
            self._username, self._password, self._month_access_token = self.get_credentials_from_config()
        else:
            self.set_user_credentials()

        self.mangadex_url_base = "https://api.mangadex.org"
        
        self.api_is_online = self.check_api_status()
        if self.api_is_online:
            self.refresh_session()

    # START AUTOMATIC FUNCTIONS

    def get_credentials_from_config(self, file="auth_config.yml"):
        if not os.path.isfile("auth_config.yml"):
            with open("auth_config.yml", "w+") as auth_configfile:
                yaml_dict = self._default_auth_config
                yaml_dict["user_credentials"]["username"], yaml_dict["user_credentials"]["password"] = self.prompt_for_user_credentials()
                yaml.safe_dump(yaml_dict, auth_configfile)
        with open("auth_config.yml") as auth_configfile:
            config_data = yaml.safe_load(auth_configfile)
            return config_data["user_credentials"]["username"], config_data["user_credentials"]["password"], config_data["refresh_token"]

    def check_api_status(self) -> bool:
        """Verify that the api auth system is online."""
        return requests.get(self.mangadex_url_base + "/auth/check").status_code == 200

    def set_user_credentials(self, username, password):
        self._username = username
        self._password = password

    def prompt_for_user_credentials(self):
        username = input("Please enter your MangaDex username: ")
        password = input("Please enter your MangaDex password: ")
        return username, password

    # Only run if refresh token is invalid
    def authenticate_user(self, username="", password=""):
        """Authenticate the user with credentials in auth_config.yml."""
        print(f"Authenticating user: {self._username}")
        request_data = {
            "username": self._username,
            "password": self._password
        }
        self.auth_info = requests.post(self.mangadex_url_base + "/auth/login", json=request_data)
        print("Authentication successful") if self.auth_info.status_code == 200 else print(f"Authentication failed, check your credentials: Error code {self.auth_info.status_code}")
        
        self._jwt = self.auth_info.json()["token"]["session"]
        self._month_access_token = self.auth_info.json()["token"]["refresh"]
        self._headers = {"Authorization": "Bearer " + self._jwt}
        # Write refresh token to auth_configfile
        yaml_dict = self._default_auth_config
        with open("auth_config.yml", "r") as auth_configfile:
             yaml_dict = yaml.safe_load(auth_configfile)
             yaml_dict["refresh_token"] = self._month_access_token
        with open("auth_config.yml", "w") as auth_configfile:
            yaml.safe_dump(yaml_dict, auth_configfile)
        
        return self.auth_info.status_code, self.auth_info

    def get_logged_user_id(self):
        """Retrieves the user id of the user with credentials in auth_config.yml."""
        response = requests.get(self.mangadex_url_base + "/user/me")
        if response.status_code == 200:
            self.user_id = response["data"]["id"]
        else:
            print(f"Error fetching user id: Error code {response.status_code}")
        return response.status_code, response
    
    # END AUTOMATIC FUNCTIONS
    # START REFRESH FUNCTIONS
    
    def refresh_session(self):
        data_json = {
            "token": self._month_access_token
        }
        response = requests.post(self.mangadex_url_base + "/auth/refresh", json=data_json)
        if response.status_code == 400:
            self.authenticate_user()
        else:
            self._jwt = response.json()["token"]["session"]
            self._month_access_token = response.json()["token"]["refresh"]
            self._headers = {"Authorization": "Bearer " + self._jwt}

    # END REFRESH FUNCTIONS
    # START EXTERNALLY-CALLED FUNCTIONS

    def get_username(self):
        return self._username

    def get_user_followed_manga_list(self):
        response = requests.get(self.mangadex_url_base + "/user/follows/manga", headers=self._headers)
        if response.status_code == 401:
            self.refresh_session()
            response = requests.get(self.mangadex_url_base + "/user/follows/manga", headers=self._headers)
        if response.status_code == 200:
            self.follows_list = response.json()["results"]
            self.followed_titles = [(manga["data"]["attributes"]["title"]["en"], manga["data"]["id"]) for manga in self.follows_list]
            return self.follows_list
        else:
            print(f"Error fetching follows list: Error code {response.status_code}")

    # END EXTERNALLY-CALLED FUNCTIONS

if __name__ == "__main__":
    profile = UserProfile()
    profile.get_user_followed_manga_list()
    print(profile.followed_titles)
