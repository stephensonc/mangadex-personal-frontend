import json 
import os
import tkinter as tk
from tkinter import filedialog
from RequestHandler import RequestHandler

class DataExporter:

    def __init__(self, request_handler=None):
        self.request_handler = request_handler if request_handler is not None else RequestHandler()
        self.credential_manager = self.request_handler.credential_manager
        self.default_directory = "exports"

    def export_follows_as_list_ui(self):
        self.export_follows_ui(file_format="list")
    def export_follows_as_json_ui(self):
        self.export_follows_ui(file_format="json")

    def export_follows_ui(self, file_format="list"):
        title = "Export Data"
        if(file_format=="list"):
            title += " as List"
        elif(file_format=="json"):
            title += " as JSON"

        filepath = self.prompt_for_export_file(
            title=title,
            initial_file="user_follows",
            file_extension=self.get_default_file_extension(file_format=file_format)
        )
        self.export_follows(file_format=file_format, file=filepath)

    def prompt_for_export_file(self, title="Export Data", start_dir="", initial_file="", file_extension=".txt"):
        if(start_dir==""):
            start_dir = self.default_directory
        if(initial_file!="" and "." not in initial_file):
            initial_file+=file_extension
        
        os.makedirs(start_dir, exist_ok=True)
        root = tk.Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        file_path = filedialog.askopenfilename(
            parent=root,
            title=title,
            initialdir=start_dir,
            initialfile=initial_file,
            defaultextension=file_extension
        )
        root.destroy()
        return file_path

    def get_default_file_extension(self, file_format="list"):
        if("json" in file_format):
            return ".json"
        elif(file_format=="list" or "txt" in file_format or file_format=="text"):
            return ".txt"
        else:
            print("Unsupported format given: " + file_format + ". Defaulting to .txt")
            return ".txt"

    def export_follows(self, file_format="list", file=""):
        """Export follows list
        
        params:
            format -> Either 'list' or 'json'
            file -> the file path to write the file to. Will default to using the "exports" folder
        """
        print("Exporting follows list")
        follows_list = self.request_handler.get_user_followed_manga_list()
        
        # Update default file extension
        if(file==""):
            file = self.default_directory + "/" + "user_follows" + self.get_default_file_extension(file_format=file_format)

        # Write to file
        with open(file, "w") as follows_file:
            if(file_format=="list"):
                follows_file.write('\n'.join(str(name) for name in follows_list.keys()))
            elif(file_format=="json"):
                follows_file.write(json.dumps(follows_list, indent=2))
        if(os.path.isfile(file)):
            print("Export successful")
        else:
            print("Export failed to create file")
                

def main():
    dataExporter = DataExporter()
    dataExporter.export_follows()
    dataExporter.export_follows(file_format="json")
    dataExporter.export_follows_ui()
    dataExporter.export_follows_ui("json")
    pass

if __name__ == "__main__":
    main()