import io
import time
from PIL import ImageTk, Image
import requests
from CredentialManager import CredentialManager


class RequestHandler:
    """Facilitate iteractions with mangadex api."""

    def __init__(self, credential_manager=None) -> None:
        self.credential_manager = credential_manager if credential_manager is not None else CredentialManager()

        self._headers = self.update_headers(self.credential_manager.access_token)
        self.mangadex_url_base = "https://api.mangadex.org"
        self.mangadex_auth_url = "https://auth.mangadex.org"
        self.refresh_session()

    def check_api_status(self) -> bool:
        """Verify that the api auth system is online."""
        return requests.get(self.mangadex_url_base + "/auth/check").status_code == 200

    # Begin User Authentication

    def authenticate_user(self, username="", password="", client_id="", client_secret=""):
        """Authenticate the user"""

        print(f"Authenticating user: {self.credential_manager.username}")
        request_data = {
            "grant_type":"password",
            "username": self.credential_manager.username if username == "" else username,
            "password": self.credential_manager.password if password == "" else password,
            "client_id": self.credential_manager.client_id if client_id == "" else client_id,
            "client_secret": self.credential_manager.client_secret if client_secret == "" else client_secret
        }
        self.auth_info = requests.post(self.mangadex_auth_url + "/realms/mangadex/protocol/openid-connect/token", data=request_data)
        if(self.auth_info.status_code == 200):
            print("Authentication successful")
             # Write refresh token to auth_configfile, keeping old values
            self.credential_manager.access_token = self.auth_info.json()["access_token"]
            self.credential_manager.refresh_token = self.auth_info.json()["refresh_token"]
            self.update_headers()
            self.credential_manager.update_tokens_in_cache(
                access_token = self.credential_manager.access_token,
                refresh_token = self.credential_manager.refresh_token
            )
        else:
            print(f"Authentication failed, check your credentials: Error code {self.auth_info.status_code}")
            error = self.auth_info.json()["error"]
            error_desc = self.auth_info.json()["error_description"]
            print(f"Error: {error}")
            print(f"Error Description: {error_desc}")
            self.credential_manager.clear_cache()
            self.refresh_session()
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
        request_data = {
            "grant_type": "refresh_token",
            "refresh_token": self.credential_manager.refresh_token,
            "client_id": self.credential_manager.client_id,
            "client_secret": self.credential_manager.client_secret
        }
        response = requests.post(self.mangadex_auth_url + "/realms/mangadex/protocol/openid-conect/token", data=request_data)
        if response.status_code == 200:
            print(response.status_code)
            self.credential_manager.access_token = response.json()["access_token"]
            self.credential_manager.update_tokens_in_cache()
            self.update_headers()
        elif response.status_code == 400:
            self.authenticate_user()
        elif response.status_code == 429:
            # Too many requests
            print(response.json())
            print("Refresh rate exceeded")
            self.refresh_session()
        else:
            if(not self.credential_manager.cache_exists()):
                print("Failed to refresh, re-prompt for credentials")
                self.credential_manager.prompt_for_credentials(lastFailed=True)
            self.authenticate_user()


    def update_headers(self, access_token=""):
        new_token = access_token if access_token != "" else self.credential_manager.access_token
        self._headers = {"Authorization": "Bearer " + new_token}

    # End User Authentication

    def get_username(self):
        return self.credential_manager.username


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
