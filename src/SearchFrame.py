from MangaViewer import MangaViewer
import tkinter as tk
from tkinter import ttk
from tkinter.constants import END, RAISED
from tkinter.messagebox import showinfo

class SearchFrame(tk.Frame):

    def __init__(self, request_handler, master=None):
        super(SearchFrame, self).__init__()

        self.request_handler = request_handler
        self.pack(side="right")

        self.manga_list = self.request_handler.get_searchable_manga_list()

        self.manga_titles = self.get_search_list()

        self.results_frame = tk.Frame(self)
        
        self.create_search_widget()
        self.create_results_widget()
    
    def create_search_widget(self):
        self.search_bar_frame = tk.Frame(self)
        self.search_bar_frame.pack(side="top")
        self.search_label = tk.Label(self.search_bar_frame, text="Search for manga", font=("Arial", 25), relief=RAISED, width=22)
        self.search_label.pack(side="top")

        self.search_query = tk.StringVar()
        self.search_query.trace('w', self.update_search_results)
        # self.search_query.trace('u', self.get_search_results)
        self.entry_bar = ttk.Combobox(self.search_bar_frame, width="40", textvariable=self.search_query)
        self.entry_bar['values'] = self.get_search_list()
        self.entry_bar.bind("<<ComboboxSelected>>", self.open_manga_from_search)
        
        self.entry_bar.pack(side="left")
        self.search_button = tk.Button(self.search_bar_frame, text="Search", command=self.fetch_search_results_from_query)
        self.search_button.pack(side="right")
    
    def create_results_widget(self):
        self.results_frame.destroy()
        self.results_frame = tk.Frame(self)
        self.results_frame.pack(side="bottom")
        self.results_box = tk.Listbox(self.results_frame, width=50, height=40)
        results_y_scroll = tk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.results_box.yview)
        results_y_scroll.pack(side="right")
        self.results_box.config(yscrollcommand=results_y_scroll.set)
        self.results_box.bind('<<ListboxSelect>>', self.open_manga_from_results_box)
        self.results_box.pack(side="bottom")


    def update_search_results(self, event=None, *args):
        self.entry_bar['values'] = [entry for entry in self.manga_titles if self.search_query.get() in entry]
    
    def get_search_list(self, *args):
        # Debug
        # for manga in self.manga_list:
        #     print(manga["data"]["attributes"]["title"])
        pre_filter_title_list = [manga["data"]["attributes"]["title"] for manga in self.manga_list]
        titles = [manga_title["en"] for manga_title in pre_filter_title_list if "en" in manga_title.keys()]
        return titles

    def fetch_search_results_from_query(self, *args):
        self.query_results = self.request_handler.get_searchable_manga_list(limit=50, title=self.search_query.get())
        query_results = [manga["data"]["attributes"]["title"]["en"] for manga in self.query_results]
        self.entry_bar["values"] = query_results
        self.create_results_widget() 
        for result in query_results:
            self.results_box.insert(END, result)

    def open_manga_from_search(self, *args):
        for manga in self.manga_list:
            if self.search_query.get() in manga["data"]["attributes"]["title"]["en"]:
                manga_id = manga["data"]["id"]
                manga_viewer = MangaViewer(request_handler=self.request_handler, manga_id=manga_id)
    
    def open_manga_from_results_box(self, *args):
        manga_title = self.results_box.get(self.results_box.curselection())
        for manga in self.query_results:
            if manga_title == manga["data"]["attributes"]["title"]["en"]:
                manga_id = manga["data"]["id"]
                manga_viewer = MangaViewer(request_handler=self.request_handler, manga_id=manga_id)
