import tkinter as tk
import html
from tkinter.constants import END, NE, NW, RAISED
import math
import re

class MangaViewer(tk.Toplevel):

    def __init__(self, request_handler, manga_id, bg="grey"):
        super(MangaViewer, self).__init__()
        # Set background color
        self.config(bg=bg)
        self.minsize(width=800,height=900)
        self.manga_id = manga_id
        # print(manga_id)

        self.request_handler = request_handler

        self.metadata = request_handler.get_manga_metadata_by_id(manga_id)        
        self.manga_title = self.metadata["attributes"]["title"]["en"]
        self.title(self.manga_title)

        self.scanlation_group = None
        self.curr_chapter = None


        self.canvas_width = 600
        self.canvas_height = 800
        self.view_frame = tk.Frame(self)
        self.create_viewer_canvas()
        
        
        self.chapter_list = request_handler.get_manga_chapter_list_by_id(manga_id)
        self.create_chapter_listbox()

    def create_viewer_canvas(self, image_url_list=[]):
        self.view_frame.destroy()
        self.view_frame = tk.Frame(self)
        self.view_frame.pack(side="right")

        self.view_pane = tk.Canvas(self.view_frame, height=self.canvas_height, width=self.canvas_width, bg='grey')

        self.canvas_scrollbar = tk.Scrollbar(self.view_frame, orient=tk.VERTICAL, command=self.view_pane.yview)
        self.view_pane.config(yscrollcommand=self.canvas_scrollbar.set)
        self.canvas_scrollbar.pack(side="right")
        self.view_pane.pack(side="top")
        self.view_pane.bind('<Enter>', self._bind_to_mousewheel)
        self.view_pane.bind('<Leave>', self._unbind_to_mousewheel)


        nav_button_frame = tk.Frame(self.view_frame)
        nav_button_frame.pack(side="bottom")
        next_button = tk.Button(nav_button_frame, text="Next", command=self.open_next_chapter)
        next_button.pack(side="right")
        prev_button = tk.Button(nav_button_frame, text="Prev", command=self.open_prev_chapter)
        prev_button.pack(side="left")

        self.images_list = []
        if image_url_list !=[]:
            idx = 1
            ycoord = 0
            for image_url in image_url_list:
                print(f"Retrieving image: {idx} of {len(image_url_list)}")
                image = self.request_handler.get_single_chapter_image_by_url(image_url)
                self.images_list.append(image)
                print(f"Adding image: {idx} of {len(image_url_list)}")
                self.view_pane.create_image(0, ycoord, anchor=NW,image=image)
                ycoord = ycoord + image.height()
                idx += 1
        self.view_pane.config(scrollregion=self.view_pane.bbox("all"))
        

    def create_chapter_listbox(self):
        self.control_frame = tk.Frame(self)
        self.control_frame.pack(side="left")

        title_label = tk.Label(self.control_frame, text=self.manga_title, font=("Arial", 15, "normal"), relief=RAISED, wraplength=400, height=2)
        title_label.pack(side="top")

        # desc = self.metadata["attributes"]["description"]["en"]
        # english_desc = desc[re.search(r"\[b\]\[u\]English\:\[\/u\]\[\/b\]", desc).end() : re.search(r"\[hr\]", desc).start()]
        # english_desc = html.unescape(english_desc)
        # desc_label = tk.Label(self.control_frame, text=english_desc, wraplength=400, font=("Helvetica", 10,"normal"))
        # print(self.metadata["attributes"]["description"]["en"])
        # desc_label.pack()

        chapter_list_label = tk.Label(self.control_frame, text="Chapter list:", relief=RAISED, font=("Arial", 25))
        chapter_list_label.pack(side="top")

        self.chapter_listbox = tk.Listbox(self.control_frame, height=40)

        total_length = 0
        for chapter in self.chapter_list:
            chap_attributes = chapter["data"]["attributes"]
            chap_num_and_title = f"{chap_attributes['chapter']} {chap_attributes['title']}"

            total_length += len(chap_num_and_title)

            self.chapter_listbox.insert(END, chap_num_and_title)
        avg_len = math.ceil(total_length / len(self.chapter_list)) + 5 if len(self.chapter_list) > 0 else 5

        self.chapter_listbox.config(width=avg_len)
        
        self.chapter_scroll = tk.Scrollbar(self.control_frame, orient=tk.VERTICAL, command=self.chapter_listbox.yview)
        self.chapter_scroll.pack(side="right")
        self.chapter_x_scroll = tk.Scrollbar(self.control_frame, orient=tk.HORIZONTAL, command=self.chapter_listbox.xview)
        self.chapter_x_scroll.pack(side="bottom")

        self.chapter_listbox.config(yscrollcommand=self.chapter_scroll.set)
        self.chapter_listbox.config(xscrollcommand=self.chapter_x_scroll.set)
        # self.chapter_listbox.bind("<<ListboxSelect>>", self.open_chapter_from_box)
        self.chapter_listbox.pack(side="bottom")

        chapter_select_button = tk.Button(self.control_frame, text="Open Selected Chapter", command=self.open_chapter_from_box)
        chapter_select_button.pack()


    def open_chapter_from_box(self, event=None):
        chapter_title = self.chapter_listbox.get(self.chapter_listbox.curselection())

        chapter_number = float(chapter_title[0:re.search(r" ", chapter_title).start()])
        self.open_chapter_by_number(number=chapter_number)

    def open_next_chapter(self):
        print(f"Current chapter number: {self.curr_chapter}")

        idx = len(self.chapter_list) - 1
        while idx > 0 and float(self.chapter_list[idx]["data"]["attributes"]["chapter"]) <= self.curr_chapter:
            idx -= 1
        next_chap_number = float(self.chapter_list[idx]["data"]["attributes"]["chapter"])
        print(f"Next chapter number: {next_chap_number}")
        self.open_chapter_by_number(next_chap_number)
    
    def open_prev_chapter(self):
        for chap in self.chapter_list:
            previous_chapter_number = float(chap["data"]["attributes"]["chapter"])
            print(self.curr_chapter)
            if previous_chapter_number < self.curr_chapter:
                print(f"Next chapter number: {previous_chapter_number}")
                self.open_chapter_by_number(previous_chapter_number)
                break

    def open_chapter_by_number(self, number):
        """Create a canvas object containing the images in the chapter corresponding with the number"""
        chapters_with_number = [chap for chap in self.chapter_list if float(chap["data"]["attributes"]["chapter"]) == number]

        chap_id = ""
        for chapter in chapters_with_number:
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
            
        self.curr_chapter = number
        chapter_image_urls = self.request_handler.get_chapter_images_by_id(chap_id)
        self.create_viewer_canvas(chapter_image_urls)
        

    def _bind_to_mousewheel(self, event):
        self.view_pane.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _unbind_to_mousewheel(self, event):
        self.view_pane.unbind_all("<MouseWheel>")
    
    def _on_mousewheel(self, event):
        self.view_pane.yview_scroll(int(-1*(event.delta/120)), "units")


        
        




        