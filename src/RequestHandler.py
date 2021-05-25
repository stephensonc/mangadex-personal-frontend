from requests.models import Response
import os
import yaml
import json
import requests


class RequestHandler:
    """Facilitate iteractions with mangadex api."""

    def __init__(self) -> None:

        self._default_auth_config = {
            "user_credentials": {"username": "", "password": ""},
            "refresh_token": ""
        }
        self._username = ""
        self._password = ""
        self._month_access_token = ""
        self._jwt = ""
        self._headers = {"Authorization": "Bearer " + self._jwt}

        self.mangadex_url_base = "https://api.mangadex.org"


    def config_exists(self, file="auth_config.yml"):
        return os.path.isfile(file)

    def get_data_from_config(self, file="auth_config.yml"):
        if self.config_exists():
            with open("auth_config.yml") as auth_configfile:
                config_data = yaml.safe_load(auth_configfile)
                return config_data
        else:
            return {}

    def check_api_status(self) -> bool:
        """Verify that the api auth system is online."""
        return requests.get(self.mangadex_url_base + "/auth/check").status_code == 200

    # Begin User Authentication

    def set_user_credentials(self, username, password):
        self._username = username
        self._password = password
        yaml_dict = self.get_data_from_config() if self.config_exists() else self._default_auth_config
        yaml_dict["user_credentials"]["username"] = username
        yaml_dict["user_credentials"]["password"] = password
        with open("auth_config.yml", "w") as configfile:
            yaml.safe_dump(yaml_dict, configfile)


    def authenticate_user(self, username="", password=""):
        """Authenticate the user"""
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


    # End User Authentication


    def get_username(self):
        return self._username

    def get_user_followed_manga_list(self):
        response = requests.get(self.mangadex_url_base + "/user/follows/manga", headers=self._headers)
        if response.status_code == 401:
            self.refresh_session()
            response = requests.get(self.mangadex_url_base + "/user/follows/manga", headers=self._headers)
        if response.status_code == 200:
            self.follows_list = response.json()["results"]
            condensed_follows = {}
            for manga in self.follows_list:
                condensed_follows.update({manga["data"]["attributes"]["title"]["en"]:{"id": manga["data"]["id"]}})
            return condensed_follows
        else:
            print(f"Error fetching follows list: Error code {response.status_code}")
    

    # Begin Manga requests

    def get_manga_metadata_by_id(self, manga_id):
        endpoint = f"{self.mangadex_url_base}/manga/{manga_id}"
        response = requests.get(endpoint)
        if "ok" in response.json()["result"]:
            return response.json()["data"]
        else:
            print(response.status_code)
            return None

    def get_manga_chapter_list_by_id(self, manga_id, order="desc"):
        endpoint = f"{self.mangadex_url_base}/manga/{manga_id}/feed"
        # print(endpoint)

        params = {
            "limit": 500,
            "translatedLanguage[]": ["en"],
            "order[volume]": order,
            "order[chapter]": order
        }

        response = requests.get(endpoint, params=params)

        # print(response.request.path_url)
        if response.status_code == 200:
            return response.json()["results"]
        else:
            print(response.json())
            return None

    def get_chapter_images_by_id(self, chapter_id):
        # print(chapter_id)
        pass


if __name__ == "__main__":
    profile = RequestHandler()
    profile.get_user_followed_manga_list()
    print(profile.followed_titles)
