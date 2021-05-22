import yaml
import requests


class UserProfile:
    
    def __init__(self) -> None:

        self.mangadex_url_base = "https://api.mangadex.org"

        with open("../config.yml") as configfile:
            self.config = yaml.safe_load(configfile)
        self.username = self.config["user_credentials"]["username"]
        self.password = self.config["user_credentials"]["password"]
