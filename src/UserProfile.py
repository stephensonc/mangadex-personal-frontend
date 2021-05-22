import yaml
import requests


class UserProfile:
    
    def __init__(self) -> None:

        self.mangadex_url_base = "https://api.mangadex.org"

        with open("config.yml") as configfile:
            self.config = yaml.safe_load(configfile)
        self.username = self.config["user_credentials"]["username"]
        self.password = self.config["user_credentials"]["password"]
        self.api_is_online = self.check_api_status()
        if self.api_is_online:
            print(f"Authentication status code: {self.authenticate_user()}")
        
    def check_api_status(self) -> bool:
        # Verify that the api auth system is online
        return requests.get(self.mangadex_url_base + "/auth/check").status_code == 200

    def authenticate_user(self) -> int:
        print(f"Authenticating user: {self.username}")
        request_data = {
            "username": self.username,
            "password": self.password
        }
        self.auth_info = requests.post(self.mangadex_url_base + "/auth/login", json=request_data)
        return self.auth_info.status_code

if __name__ == "__main__":
    profile = UserProfile()
