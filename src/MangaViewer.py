import tkinter as tk
from MangaManager import MangaManager

class MangaViewer(tk.Toplevel):

    def __init__(self, manga_id):
        super(MangaViewer, self).__init__()
        
        self.manga_manager = MangaManager(manga_id)
        
        self.control_frame = tk.Frame(self)
        self.control_frame.pack(side="left")
        
        self.chapter_listbox = tk.Listbox(self.control_frame)
        chapter_scroll = tk.Scrollbar(self.chapter_listbox)
        chapter_scroll.config(command=self.chapter_listbox.yview)
        self.chapter_listbox.config(yscrollcommand=chapter_scroll.set)
        




        