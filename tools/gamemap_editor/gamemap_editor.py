from pathlib import Path
from typing import Callable, Optional
from tkinter import filedialog
import tkinter as tk
import json
import sys
import os

sys.path.append(str(Path(__file__).parent.parent.parent))

from mergic import GameMap, AssetFinder, ImageAtlas

class GameMapEditor:
    def __init__(self, gamemap: Optional[GameMap] = None, on_import_gamemap: Optional[Callable[[GameMap], None]] = None):
        self.gamemap_buffer: Optional[GameMap] = gamemap
        self.on_import_gamemap: Optional[Callable[[GameMap]]] = on_import_gamemap

    def import_gamemap_from_file(self, filepath: str | os.PathLike):
        with open(filepath, "r") as f:
            gamemap = json.load(f)
            self.gamemap_buffer = GameMap(
                gamemap["width"], gamemap["height"], layers=gamemap["layers"]
            )
        if self.on_import_gamemap:
            self.on_import_gamemap(self.gamemap_buffer)
    
    def display_layerlist(self):
        return list(self.gamemap_buffer.layers.keys())



class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mergic GameMap Editor")
        self.root.geometry("640x540")
        self.gamemap_editor = GameMapEditor()
    
    def dialog_openfile(self):
        filepath = filedialog.askopenfilename(defaultextension=".json", filetypes=[("GameMap(.json)", "*.json")])
        if filepath:
            self.gamemap_editor.import_gamemap_from_file(filepath)
            

    def setup(self):
        menubar = tk.Menu(self.root)
        self.root.configure(menu=menubar)
        menu_file = tk.Menu(menubar)
        menu_file.add_cascade(label="New")
        menu_file.add_cascade(label="Save")
        menu_file.add_cascade(label="Open", command=self.dialog_openfile)
        menubar.add_cascade(label="File", menu=menu_file)

        pained_window = tk.PanedWindow(self.root, sashwidth=4, sashrelief=tk.SOLID)

        non_mapeditor_area = tk.Frame(self.root)
        # pallete
        pallate_frame = tk.Frame(non_mapeditor_area, bd=1, relief=tk.RAISED)
        brush_list = tk.Listbox(pallate_frame, selectmode=tk.SINGLE)
        tk.Label(pallate_frame, text="Pallate").pack()
        preview_widget = tk.Label()
        preview_widget.pack()
        brush_list.pack()
        pallate_frame.pack(pady=2)
        # layer editor
        layer_editor_frame = tk.Frame(non_mapeditor_area, bd=1, relief=tk.RAISED)
        tk.Label(layer_editor_frame, text="Layers").pack()
        layerlist_buffer = tk.StringVar()
        layer_list = tk.Listbox(layer_editor_frame, selectmode=tk.SINGLE, listvariable=layerlist_buffer)
        self.gamemap_editor.on_import_gamemap = lambda gamemap: layerlist_buffer.set(self.gamemap_editor.display_layerlist())
        btns_to_edit_layer_name_frame = tk.Frame(layer_editor_frame)
        btn_add_layer = tk.Button(btns_to_edit_layer_name_frame, text="Add")
        btn_rename_layer = tk.Button(btns_to_edit_layer_name_frame, text="Rename")
        entry_layer_name = tk.Entry(layer_editor_frame)
        btn_delete_layer = tk.Button(layer_editor_frame, text="Delete")
        btn_add_layer.pack(side=tk.LEFT)
        btn_rename_layer.pack(side=tk.LEFT)
        btns_to_edit_layer_name_frame.pack()
        entry_layer_name.pack()
        layer_list.pack()
        btn_delete_layer.pack()
        layer_editor_frame.pack()
        # --
        non_mapeditor_area.pack()

        map_editor_frame = tk.Frame(self.root, bd=1)
        map_editor_canvas = tk.Canvas(map_editor_frame, bg="#000000")
        map_editor_canvas.pack(fill=tk.BOTH, expand=True)
        map_editor_frame.pack(side=tk.RIGHT)

        pained_window.add(non_mapeditor_area)
        pained_window.add(map_editor_frame)
        pained_window.pack(expand=True, fill=tk.BOTH)

    def run(self):
        self.setup()
        self.root.mainloop()
