from requests.models import Response
import yaml
import requests


class UserProfile:
    
    def __init__(self) -> None:

        self.mangadex_url_base = "https://api.mangadex.org"

        with open("config.yml") as configfile:
            self.config = yaml.safe_load(configfile)
        self.username = self.config["user_credentials"]["username"]
        self.password = self.config["user_credentials"]["password"]
        self.refresh_token = self.config["refresh_token"]
        self.api_is_online = self.check_api_status()
        if self.api_is_online:
            self.refresh_session()


    # START AUTOMATIC FUNCTIONS

    def check_api_status(self) -> bool:
        # Verify that the api auth system is online
        return requests.get(self.mangadex_url_base + "/auth/check").status_code == 200

    # Only run if refresh token is invalid
    def authenticate_user(self):
        print(f"Authenticating user: {self.username}")
        request_data = {
            "username": self.username,
            "password": self.password
        }
        self.auth_info = requests.post(self.mangadex_url_base + "/auth/login", json=request_data)
        print("Authentication successful") if self.auth_info.status_code == 200 else print("Authentication failed, check your credentials")
        
        self.jwt = self.auth_info.json()["token"]["session"]
        self.month_access_token = self.auth_info.json()["token"]["refresh"]
        self.headers = {"Authorization": "Bearer " + self.jwt}
        # Write refresh token to configfile
        yaml_dict = {
            "user_credentials": {"username": "", "password": ""},
            "refresh_token": ""
        }
        with open("config.yml", "r") as configfile:
             yaml_dict = yaml.safe_load(configfile)
             yaml_dict["refresh_token"] = self.refresh_token
        with open("config.yml", "w") as configfile:
            yaml.safe_dump(yaml_dict, configfile)
        
        return self.auth_info.status_code, self.auth_info

    def get_logged_user_id(self):
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
            "token": self.refresh_token
        }
        response = requests.post(self.mangadex_url_base + "/auth/refresh", json=data_json)
        if response.status_code == 400:
            self.authenticate_user()
        else:
            self.jwt = response.json()["token"]["session"]
            self.refresh_token = response.json()["token"]["refresh"]
            self.headers = {"Authorization": "Bearer " + self.jwt}

    # END REFRESH FUNCTIONS
    def get_user_followed_manga_list(self):
        response = requests.get(self.mangadex_url_base + "/user/follows/manga", headers=self.headers)
        if response.status_code == 401:
            self.refresh_session()
            response = requests.get(self.mangadex_url_base + "/user/follows/manga", headers=self.headers)
        if response.status_code == 200:
            self.follows_list = response.json()["results"]
            self.followed_titles = [(manga["data"]["attributes"]["title"]["en"], manga["data"]["id"]) for manga in self.follows_list]
            return self.follows_list
        else:
            print(f"Error fetching follows list: Error code {response.status_code}")



if __name__ == "__main__":
    profile = UserProfile()
    profile.get_user_followed_manga_list()
    print(profile.followed_titles)
