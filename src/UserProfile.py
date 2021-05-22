import yaml

class UserProfile:
    
    def __init__(self) -> None:
        with open("../credentials.yml") as configfile:
            self.config = yaml.safe_load(configfile)
        self.username = 
