import tkinter as tk
from tkinter.constants import END
import math
import re

class MangaViewer(tk.Toplevel):

    def __init__(self, request_handler, manga_id):
        super(MangaViewer, self).__init__()

        self.minsize(width=800,height=900)
        self.manga_id = manga_id

        self.request_handler = request_handler

        self.metadata = request_handler.get_manga_metadata_by_id(manga_id)        
        self.manga_title = self.metadata["attributes"]["title"]["en"]
        self.title(self.manga_title)

        self.scanlation_group = None
        
        
        self.chapter_list = request_handler.get_manga_chapter_list_by_id(manga_id)
        self.create_chapter_listbox()

    def create_chapter_listbox(self):
        self.control_frame = tk.Frame(self)
        self.control_frame.pack(side="left")
        chapter_list_label = tk.Label(self.control_frame, text="Chapter list:")
        chapter_list_label.pack(side="top")

        self.chapter_listbox = tk.Listbox(self.control_frame, height=50)

        total_length = 0
        for chapter in self.chapter_list:
            chap_attributes = chapter["data"]["attributes"]
            chap_num_and_title = f"{chap_attributes['chapter']} {chap_attributes['title']}"

            total_length += len(chap_num_and_title)

            self.chapter_listbox.insert(END, chap_num_and_title)
        avg_len = math.ceil(total_length / len(self.chapter_list)) + 5

        self.chapter_listbox.config(width=avg_len)
        
        chapter_scroll = tk.Scrollbar(self.control_frame, orient=tk.VERTICAL, command=self.chapter_listbox.yview)
        chapter_scroll.pack(side="right")
        chapter_x_scroll = tk.Scrollbar(self.control_frame, orient=tk.HORIZONTAL, command=self.chapter_listbox.xview)
        chapter_x_scroll.pack(side="bottom")

        self.chapter_listbox.config(yscrollcommand=chapter_scroll.set)
        self.chapter_listbox.config(xscrollcommand=chapter_x_scroll.set)
        self.chapter_listbox.bind("<<ListboxSelect>>", self.open_chapter_from_box)
        self.chapter_listbox.pack(side="bottom")


    def open_chapter_from_box(self, event=None):
        chapter_title = self.chapter_listbox.get(self.chapter_listbox.curselection())

        chapter_number = float(chapter_title[0:re.search(r" ", chapter_title).start()])
        self.open_chapter_by_number(number=chapter_number)

    
    def open_chapter_by_number(self, number):
        chapters_with_number = [chap for chap in self.chapter_list if float(chap["data"]["attributes"]["chapter"]) == number]

        chap_id = ""
        for chapter in chapters_with_number:
            chap_attr = chapter["data"]["attributes"]
            for relationship in chapter["relationships"]:
                if relationship["type"] == "scanlation_group":
                    group = relationship["id"]

            if self.scanlation_group is None:
                self.scanlation_group = group
                chap_id = chapter["data"]["id"]
            elif self.scanlation_group != group and chapter == chapters_with_number[-1]:
                self.scanlation_group = group
                chap_id = chapter["data"]["id"]
            elif self.scanlation_group == group:
                chap_id = chapter["data"]["id"]
            
        chapter_images = self.request_handler.get_chapter_by_id(chap_id)
        

                



        
        




        