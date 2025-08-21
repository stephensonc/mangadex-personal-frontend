import io
import time
import os
import yaml
from PIL import ImageTk, Image
import requests


class RequestHandler:
    """Facilitate iteractions with mangadex api."""

    def __init__(self) -> None:

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
        self._username = ""
        self._password = ""
        self._client_id = ""
        self._client_secret = ""
        self._access_token = ""
        self._refresh_token = ""
        self._headers = self.update_headers()

        self.mangadex_url_base = "https://api.mangadex.org"
        self.mangadex_auth_url = "https://auth.mangadex.org"


    def config_exists(self, file="auth_config.yml"):
        file_exists = os.path.isfile(file)
        if not file_exists:
            return False
        else:
            config_dict = {}
            with open(file) as auth_configfile:
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

    def get_data_from_config(self, file="auth_config.yml"):
        if self.config_exists():
            with open(file) as auth_configfile:
                config_data = yaml.safe_load(auth_configfile)
                return config_data
        else:
            return {}

    def check_api_status(self) -> bool:
        """Verify that the api auth system is online."""
        return requests.get(self.mangadex_url_base + "/auth/check").status_code == 200

    # Begin User Authentication

    def set_user_credentials(self, username, password, client_id, client_secret):
        self._username = username
        self._password = password
        self._client_id = client_id
        self._client_secret = client_secret
        yaml_dict = self.get_data_from_config() if self.config_exists() else self._default_auth_config
        yaml_dict["user_credentials"]["username"] = username
        yaml_dict["user_credentials"]["password"] = password
        yaml_dict["user_credentials"]["client_id"] = client_id
        yaml_dict["user_credentials"]["client_secret"] = client_secret
        with open("auth_config.yml", "w") as configfile:
            yaml.safe_dump(yaml_dict, configfile)


    def authenticate_user(self, username="", password="", client_id="", client_secret=""):
        """Authenticate the user"""
        yaml_dict = self._default_auth_config

        print(f"Authenticating user: {self._username}")
        request_data = {
            "grant_type":"password",
            "username": self._username if username == "" else username,
            "password": self._password if password == "" else password,
            "client_id": self._client_id if client_id == "" else client_id,
            "client_secret": self._client_secret if client_secret == "" else client_secret
        }
        self.auth_info = requests.post(self.mangadex_auth_url + "/realms/mangadex/protocol/openid-connect/token", data=request_data)
        if(self.auth_info.status_code == 200):
            print("Authentication successful")
             # Write refresh token to auth_configfile, keeping old values
            self._access_token = self.auth_info.json()["access_token"]
            self._refresh_token = self.auth_info.json()["refresh_token"]
            self.update_headers()
            self.update_tokens_in_cache(
                access_token = self._access_token,
                refresh_token = self._refresh_token
            )
        else:
            print(f"Authentication failed, check your credentials: Error code {self.auth_info.status_code}")
            error = self.auth_info.json()["error"]
            error_desc = self.auth_info.json()["error_description"]
            print(f"Error: {error}")
            print(f"Error Description: {error_desc}")
            # Reset the cached credentials
            yaml_dict = self._default_auth_config
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


    def update_tokens_in_cache(self, access_token="", refresh_token="", file="auth_config.yml"):
        yaml_dict = self._default_auth_config
        with open(file, "r") as auth_configfile:
            yaml_dict = yaml.safe_load(auth_configfile)
            yaml_dict["access_token"] = access_token if access_token!="" else self._access_token
            yaml_dict["refresh_token"] = refresh_token if refresh_token!="" else self._refresh_token
        with open(file, "w") as auth_configfile:
            yaml.safe_dump(yaml_dict, auth_configfile)


    def refresh_session(self):
        """Refresh the temporary access token."""
        request_data = {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
            "client_id": self._client_id,
            "client_secret": self._client_secret
        }
        response = requests.post(self.mangadex_auth_url + "/realms/mangadex/protocol/openid-conect/token", data=request_data)
        if response.status_code == 400 or response.status_code == 404:
            self.authenticate_user()
        elif response.status_code == 429:
            # Too many requests
            print(response.json())
            print("Refresh rate exceeded")
            self.refresh_session()
        else:
            print(response.status_code)
            self._access_token = response.json()["access_token"]
            self.update_headers()
            self.update_tokens_in_cache()

    def update_headers(self, access_token=""):
        new_token = access_token if access_token != "" else self._access_token
        self._headers = {"Authorization": "Bearer " + new_token}

    # End User Authentication


    def get_username(self):
        return self._username


    def get_user_followed_manga_list(self, limit=100, offset=0):
        request_data = {
            "limit":limit,
            "offset":offset
        }
        response = requests.get(self.mangadex_url_base + "/user/follows/manga", headers=self._headers, params=request_data)
        if response.status_code == 401:
            self.refresh_session()
            response = requests.get(self.mangadex_url_base + "/user/follows/manga", headers=self._headers, params=request_data)
        if response.status_code == 200:
            self.follows_list = response.json()["data"]
            condensed_follows = {}
            for manga in self.follows_list:
                condensed_manga = {}
                try:
                    condensed_manga = {
                        manga["attributes"]["title"]["en"]:{"id": manga["id"]}
                    }
                except:
                    first_available_language_title =""
                    for key in manga["attributes"]["title"]:
                        first_available_language_title = manga["attributes"]["title"][key]
                        break
                    condensed_manga = {
                        first_available_language_title:{"id": manga["id"]}
                    }
                condensed_follows.update(condensed_manga)
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
            return response.json()["data"]
        else:
            print(response.json())
            return None

    def get_chapter_images_by_id(self, chapter_id, width=600, height=800,quality_mode="dataSaver"):

        url_quality = quality_mode if quality_mode == "data" else "dataSaver"

        image_urls = []
        chapter_response = requests.get(f"{self.mangadex_url_base}/chapter/{chapter_id}")
        if chapter_response.status_code == 200:
            attributes = chapter_response.json()["data"]["attributes"]
            #hash = attributes["hash"]
            #at_home_ids = attributes[quality_mode]
            # Should contain the base_url for the image server
            at_home_response = requests.get(f"{self.mangadex_url_base}/at-home/server/{chapter_id}")

            if at_home_response.status_code == 200:
                for chapter_image_filename in at_home_response.json()["chapter"][url_quality]:
                    at_home_base_url = at_home_response.json()["baseUrl"]
                    hash = at_home_response.json()["chapter"]["hash"]
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
            #pre_processed_img = Image.open(requests.get(request_url, stream=True).raw)
            resp = requests.get(request_url, stream=True)
            dataBytes = io.BytesIO(resp)
            pre_processed_img = Image.open(dataBytes)
            
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
            return response.json()["data"]
        else:
            return []
