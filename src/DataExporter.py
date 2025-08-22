from RequestHandler import RequestHandler
import json

class DataExporter:

    def __init__(self, request_handler=None):
        self.request_handler = request_handler if request_handler is not None else RequestHandler()
        self.credential_manager = self.request_handler.credential_manager


    def export_follows_list(self, file="exports/user_follows.txt"):
        print("Exporting follows list")
        follows_list = self.request_handler.get_user_followed_manga_list().keys()
        with open(file, "w") as follows_file:
            follows_file.write('\n'.join(str(name) for name in follows_list))
        
    def export_follows_json(self, file="exports/user_follows.json"):
        print("Exporting follows list")
        follows_list = self.request_handler.get_user_followed_manga_list()
        with open(file, "w") as follows_file:
            follows_file.write(json.dumps(follows_list, indent=2))

def main():
    dataExporter = DataExporter()
    dataExporter.export_follows_json()
    dataExporter.export_follows_list()
    pass

if __name__ == "__main__":
    main()