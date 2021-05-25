import time
import sys
from requests.models import Response
import os
import yaml
from PIL import ImageTk, Image
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
        """Refresh the temporary access token."""
        data_json = {
            "token": self._month_access_token
        }
        response = requests.post(self.mangadex_url_base + "/auth/refresh", json=data_json)
        if response.status_code == 400:
            self.authenticate_user()
        elif response.status_code == 429:
            # Too many requests
            print(response.json())
            print("Refresh rate exceeded")
            self.refresh_session()
        else:
            print(response.status_code)
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

    def get_chapter_images_by_id(self, chapter_id, width=600, height=800,quality_mode="dataSaver"):

        url_quality = quality_mode if quality_mode == "data" else "data-saver"

        image_urls = []
        chapter_response = requests.get(f"{self.mangadex_url_base}/chapter/{chapter_id}")
        if chapter_response.status_code == 200:
            attributes = chapter_response.json()["data"]["attributes"]
            hash = attributes["hash"]
            at_home_ids = attributes[quality_mode]
            # Should contain the base_url for the image server
            at_home_response = requests.get(f"{self.mangadex_url_base}/at-home/server/{chapter_id}")

            if at_home_response.status_code == 200:
                for chapter_image_filename in at_home_ids:
                    at_home_base_url = at_home_response.json()["baseUrl"]
                    request_url = f"{at_home_base_url}/{url_quality}/{hash}/{chapter_image_filename}"
                    image_urls.append(request_url)
            else:
                print(f"Error fetching base_url from at-home url: Error code: {at_home_response.status_code}")
                print(at_home_response.json())
        else:
            print(f"Error fetching chapter from id: Error Code: {chapter_response.status_code}")
        return image_urls


    def get_single_chapter_image_by_url(self, request_url, width=600, height=800):
        image_url_response = requests.get(request_url)
        # print(f"Fetching image from url: {request_url}")
        
        start_time = int(time.time() * 1000)
        image = None
        num_bytes = 0
        if image_url_response.status_code == 200:
            pre_processed_img = Image.open(requests.get(request_url, stream=True).raw)
            
            original_size_img = ImageTk.PhotoImage(pre_processed_img)
            num_bytes = original_size_img.width() * original_size_img.height()
            
            # Resize image to fit within confines of MangaViewer
            image = ImageTk.PhotoImage(pre_processed_img.resize((width, height), Image.ANTIALIAS))
        end_time = int(time.time() * 1000)
        time_elapsed = end_time - start_time

        report_json = {
            "url": request_url,
            "success": image_url_response.status_code == 200,
            "cached": "x-cache" in image_url_response.headers.keys() and "HIT" in image_url_response.headers["X-Cache"],
            "bytes": num_bytes,
            "duration": time_elapsed
        }  
        # Provide feedback to the at-home source
        report_url = f"https://api.mangadex.network/report"
        report_response = requests.post(report_url, json=report_json)
        if report_response.status_code != 200:
            print(report_response.status_code)
        
        return image

    def get_searchable_manga_list(self, title=None, authors=None, artists=None, year=None, includedTags=None, includedTagsMode=None, limit=100):
        arg_list = locals()
        arg_list.pop("self")
        args = arg_list.keys()
        params = {}
        for arg in args:
            if arg_list[arg] is not None:
                params.update({arg: arg_list[arg]})
        response = requests.get(f"{self.mangadex_url_base}/manga", params=params)
        if response.status_code == 200:
            return response.json()["results"]
        else:
            return []
