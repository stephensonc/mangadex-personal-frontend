from pathlib import Path
import tkinter as tk
from PIL import ImageTk, Image
import traceback
from RequestHandler import RequestHandler
from tkinter.constants import END, NE, NW, RAISED
import math
import re
import os

class MangaViewer(tk.Toplevel):

    def __init__(self, request_handler: RequestHandler, manga_id, bg="grey"):
        super(MangaViewer, self).__init__()
        # Set background color
        self.config(bg=bg)
        self.minsize(width=800,height=900)
        self.manga_id = manga_id
        # print(manga_id)

        self.request_handler = request_handler

        self.metadata = request_handler.get_manga_metadata_by_id(manga_id)
        try:        
            self.manga_title = self.metadata["attributes"]["title"]["en"]
        except:
            first_available_language_title =""
            for key in self.metadata["attributes"]["title"]:
                first_available_language_title = self.metadata["attributes"]["title"][key]
                break
            self.manga_title = first_available_language_title
        self.title(self.manga_title)

        self.scanlation_group = None
        self.curr_chapter = None
        self.curr_chapter_name = ""

        self.cache_folder = "cached_images/"+(self.manga_title.replace('/','_').replace(' ', '_'))

        self.chapter_list = request_handler.get_manga_chapter_list_by_id(manga_id)
        self.create_chapter_listbox()

        self.canvas_width = 600
        self.canvas_height = 800
        self.view_frame = tk.Frame(self)
        self.create_viewer_canvas()

    def create_viewer_canvas(self, image_url_list=[], chapter_name=""):
        self.view_frame.destroy()
        self.view_frame = tk.Frame(self)
        self.view_frame.pack(side=tk.RIGHT, fill=tk.Y)

        chapter_title_text = ""
        if(self.curr_chapter is None):
            chapter_title_text = self.curr_chapter_name
        elif(self.curr_chapter_name is None):
            chapter_title_text = str(self.curr_chapter)
        else:
            chapter_title_text =  str(self.curr_chapter) + ": " + self.curr_chapter_name

        self.chapter_label=tk.Label(self.view_frame, text=chapter_title_text, relief=RAISED, font=("Arial", 25))
        self.chapter_label.pack(side=tk.TOP, fill=tk.X)
        self.view_pane = tk.Canvas(self.view_frame, bg='grey', height=self.canvas_height, width=self.canvas_width)
        nav_button_frame = tk.Frame(self.view_frame)
        prev_button = tk.Button(nav_button_frame, text="Prev", command=self.open_prev_chapter)
        next_button = tk.Button(nav_button_frame, text="Next", command=self.open_next_chapter)
        self.canvas_scrollbar = tk.Scrollbar(self.view_frame, orient=tk.VERTICAL, command=self.view_pane.yview)
        
        self.view_pane.config(yscrollcommand=self.canvas_scrollbar.set)
        self.canvas_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.view_pane.pack(side=tk.TOP, fill=tk.BOTH)
         
        nav_button_frame.pack(side=tk.BOTTOM, expand=False)
        prev_button.pack(side=tk.LEFT, expand=True)
        next_button.pack(side=tk.RIGHT, expand=True)

        self.images_list = []
        idx = 1
        ycoord = 0
        for image_url in image_url_list:
            # print(f"Retrieving image: {idx} of {len(image_url_list)}")
            image_path, file_extension = os.path.splitext(image_url)
            cached_filename = image_path[image_path.rindex("/"):image_path.rindex("-")]+file_extension
            sanitized_chapter = str(self.curr_chapter).replace('.','_')
            cached_filepath = self.cache_folder+"/"+sanitized_chapter+"/"+cached_filename
            pre_processed_img = None

            # Use cached file if it exists  
            if(os.path.exists(cached_filepath)):
                pre_processed_img = Image.open(cached_filepath)
            else:
                image_bytes = self.request_handler.get_single_chapter_image_bytes_by_url(image_url)
                pre_processed_img = Image.open(self.cache_image(image_bytes, cached_filepath))
            
            if(pre_processed_img is None):
                print("Failed to find image in cache or on server")
                return
            
            ycoord = self.add_image_to_viewer(self.view_pane, ycoord, pre_processed_img)
            idx += 1

    def add_image_to_viewer(self, canvas:tk.Canvas, ycoord, pre_processed_img):
        # Resize image to fit within confines of MangaViewer
        image = ImageTk.PhotoImage(pre_processed_img.resize((self.canvas_width, self.canvas_height), Image.LANCZOS))                
        self.images_list.append(image)
        # print(f"Adding image: {idx} of {len(image_url_list)}")
        canvas.create_image(0, ycoord, anchor=NW,image=image)
        self.updateScrollRegion(canvas=self.view_pane)
        ycoord = ycoord + image.height()
        return ycoord
    
    def updateScrollRegion(self, canvas: tk.Canvas):
        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox(tk.ALL))
        canvas.update()
        canvas.update_idletasks()
        
        

    def cache_image(self, imageBytes, image_file_path:str):
        try:
            os.makedirs(image_file_path[:image_file_path.rindex("/")], exist_ok=True)
            with open(image_file_path, "wb") as tmp_img_file:
                tmp_img_file.write(imageBytes)
        except:
            print("Failed to cache chapter image:\n"+traceback.format_exc())
        return image_file_path

    def create_chapter_listbox(self):
        self.control_frame = tk.Frame(self)
        self.control_frame.pack(side="left", fill=tk.Y)

        title_label = tk.Label(self.control_frame, text=self.manga_title, font=("Arial", 15), relief=RAISED, wraplength=400, height=2)
        title_label.pack(side=tk.TOP, fill=tk.X)

        # desc = self.metadata["attributes"]["description"]["en"]
        # english_desc = desc[re.search(r"\[b\]\[u\]English\:\[\/u\]\[\/b\]", desc).end() : re.search(r"\[hr\]", desc).start()]
        # english_desc = html.unescape(english_desc)
        # desc_label = tk.Label(self.control_frame, text=english_desc, wraplength=400, font=("Helvetica", 10,"normal"))
        # print(self.metadata["attributes"]["description"]["en"])
        # desc_label.pack()

        chapter_list_label = tk.Label(self.control_frame, text="Chapter list:", relief=RAISED, font=("Arial", 25))
        chapter_list_label.pack(side="top")

        self.chapter_listbox = tk.Listbox(self.control_frame)

        total_length = 0
        for chapter in self.chapter_list:
            chap_attributes = chapter["attributes"]
            chap_num_and_title = f"{chap_attributes['chapter']} {chap_attributes['title']}"

            total_length += len(chap_num_and_title)

            self.chapter_listbox.insert(END, chap_num_and_title)
        avg_len = math.ceil(total_length / len(self.chapter_list)) + 5 if len(self.chapter_list) > 0 else 5

        self.chapter_listbox.config(width=avg_len)
        
        self.chapter_scroll = tk.Scrollbar(self.control_frame, orient=tk.VERTICAL, command=self.chapter_listbox.yview)
        self.chapter_scroll.pack(side="right", fill=tk.Y)
        self.chapter_x_scroll = tk.Scrollbar(self.control_frame, orient=tk.HORIZONTAL, command=self.chapter_listbox.xview)
        self.chapter_x_scroll.pack(side="bottom", fill=tk.X)

        self.chapter_listbox.config(yscrollcommand=self.chapter_scroll.set)
        self.chapter_listbox.config(xscrollcommand=self.chapter_x_scroll.set)
        # self.chapter_listbox.bind("<<ListboxSelect>>", self.open_chapter_from_box)
        
        chapter_select_button = tk.Button(self.control_frame, text="Open Selected Chapter", command=self.open_chapter_from_box)
        chapter_select_button.pack(side=tk.TOP)
        self.chapter_listbox.pack(side=tk.TOP, fill=tk.Y, expand=True)




    def open_chapter_from_box(self, event=None):
        chapter_title = self.chapter_listbox.get(self.chapter_listbox.curselection())
        chapter_number = float(chapter_title[0:re.search(r" ", chapter_title).start()])
        if(str(chapter_number).endswith(".0")):
            chapter_number = int(chapter_number)
        self.open_chapter_by_number(number=chapter_number)

    def open_next_chapter(self):
        print(f"Current chapter number: {self.curr_chapter}")

        idx = len(self.chapter_list) - 1
        while idx > 0 and float(self.chapter_list[idx]["attributes"]["chapter"]) <= self.curr_chapter:
            idx -= 1
        next_chap_number = float(self.chapter_list[idx]["attributes"]["chapter"])
        print(f"Next chapter number: {next_chap_number}")
        self.open_chapter_by_number(next_chap_number)
    
    def open_prev_chapter(self):
        for chap in self.chapter_list:
            previous_chapter_number = float(chap["attributes"]["chapter"])
            print(self.curr_chapter)
            if previous_chapter_number < self.curr_chapter:
                print(f"Next chapter number: {previous_chapter_number}")
                self.open_chapter_by_number(previous_chapter_number)
                break

    def open_chapter_by_number(self, number):
        """Create a canvas object containing the images in the chapter corresponding with the number"""
        chapters_with_number = [chap for chap in self.chapter_list if float(chap["attributes"]["chapter"]) == number]

        chap_id = ""
        group = None
        title = ""
        for chapter in chapters_with_number:
            for relationship in chapter["relationships"]:
                if relationship["type"] == "scanlation_group":
                    group = relationship["id"]
            if group is None:
                group = "N/A"
            title = chapter["attributes"]["title"]

            if self.scanlation_group is None:
                self.scanlation_group = group
                chap_id = chapter["id"]
            elif self.scanlation_group != group and chapter == chapters_with_number[-1]:
                self.scanlation_group = group
                chap_id = chapter["id"]
            elif self.scanlation_group == group:
                chap_id = chapter["id"]
            
            
        self.curr_chapter = number
        self.curr_chapter_name = title
        chapter_image_urls = self.request_handler.get_chapter_image_urls_by_id(chap_id)
        self.create_viewer_canvas(chapter_image_urls, self.curr_chapter_name)

        
        




        