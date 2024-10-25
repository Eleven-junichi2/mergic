from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
from typing import Optional

import pygame
from mergic.asset import AssetFinder, ImageAtlas
from mergic.gamemap import (
    TileMap,
    register_imgs_and_existing_regions_files_in_dirs,
    build_tileid_to_surf_from_img_dirs,
)

from tkinter import ttk
import tkinter as tk

from PIL import Image, ImageTk


CONFIG_FILEPATH = Path(__file__).parent / "config.json"


# --initialization
@dataclass
class Config:
    # Define default configuration
    tile_width: int = 16
    tile_height: int = 16
    tile_img_dirpaths: list[str | os.PathLike] = field(
        default_factory=lambda: [
            str(
                Path(__file__).parent.parent.parent
                / "mergic"
                / "assets"
                / "imgs"
                / "tiles"
            )
        ]
    )


if not CONFIG_FILEPATH.exists():
    config = Config()
    with open(CONFIG_FILEPATH, "w") as f:
        json.dump(asdict(config), f, indent=4)
else:
    with open(CONFIG_FILEPATH, "r", encoding="utf-8") as f:
        config = Config(**json.load(f))

asset_finder = AssetFinder()
tileids = register_imgs_and_existing_regions_files_in_dirs(
    config.tile_img_dirpaths, asset_finder
)[0]
tileid_to_surf = build_tileid_to_surf_from_img_dirs(
    asset_finder, tile_img_assets_as_tileids=tileids
)
traits = []

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tile Map Viewer")
        self.root.geometry("640x540")
        self.brush_listvar = tk.StringVar()
        self.brush_listvar.set(list(tileid_to_surf.keys()))
        self.layer_listvar = tk.StringVar()
        self.layer_type_list = ["trait", "terrain"]
        self.layer_type_strvar = tk.StringVar()
        self.layer_type_strvar.set(self.layer_type_list[0])
        self.traitbrush_strvar = tk.StringVar()
        self.trait_entry: Optional[tk.Entry] = None
        self.tilemap = TileMap()

    def setup(self):
        # menu
        menubar = tk.Menu(self.root)
        self.root.configure(menu=menubar)
        menu_file = tk.Menu(menubar)
        menu_file.add_cascade(label="New")
        menu_file.add_cascade(label="Save")
        menu_file.add_cascade(label="Open")
        menubar.add_cascade(label="File", menu=menu_file)
        # --
        pained_window = tk.PanedWindow(self.root, sashwidth=4, sashrelief=tk.SOLID)

        # non map editor frame
        non_map_editor_frame = tk.Frame(self.root)
        # pallate frame
        pallate_frame = tk.Frame(non_map_editor_frame, bd=1, relief=tk.RAISED)
        brush_listbox = tk.Listbox(
            pallate_frame, selectmode=tk.SINGLE, listvariable=self.brush_listvar
        )
        tk.Label(pallate_frame, text="Pallate").pack()
        preview_widget = tk.Label(pallate_frame)
        brush_listbox.bind(
            "<<ListboxSelect>>",
            lambda event: self.on_select_brush(event, preview_widget),
        )
        preview_widget.pack()
        brush_listbox.pack(expand=True)
        pallate_frame.pack()
        # --
        # layers frame
        layers_frame = tk.Frame(non_map_editor_frame, bd=1)
        tk.Label(layers_frame, text="layer type").pack()
        # layer_type_listbox = tk.Listbox(
        #     layers_frame, selectmode=tk.SINGLE, listvariable=self.layer_type_listvar
        # )
        layer_type_combobox = ttk.Combobox(layers_frame, values=self.layer_type_list, textvariable=self.layer_type_strvar)
        layer_type_combobox.bind(
            "<<ComboboxSelected>>", lambda event: self.on_select_layer_type(event)
        )
        tk.Label(layers_frame, text="layer").pack()
        layer_listbox = tk.Listbox(
            layers_frame,
            selectmode=tk.SINGLE,
            listvariable=self.layer_listvar,
        )
        layer_listbox.bind(
            "<<ListboxSelect>>", lambda event: self.on_select_layer(event)
        )
        layer_type_combobox.pack()
        layer_listbox.pack()
        layers_frame.pack()
        # --
        non_map_editor_frame.pack()
        # ---

        # map editor frame
        map_editor_frame = tk.Frame(self.root, bd=1)
        map_editor_canvas = tk.Canvas(map_editor_frame)
        y_scrollbar = tk.Scrollbar(
            map_editor_canvas, orient=tk.VERTICAL, command=map_editor_canvas.yview
        )
        x_scrollbar = tk.Scrollbar(
            map_editor_canvas, orient=tk.HORIZONTAL, command=map_editor_canvas.xview
        )
        map_editor_canvas.configure(
            scrollregion=(0, 0, 900, 900)
        )  # TODO: Fix scrollregion to reflect the size of the gamemap.
        map_editor_canvas.configure(yscrollcommand=y_scrollbar.set)
        map_editor_canvas.configure(xscrollcommand=x_scrollbar.set)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        map_editor_canvas.pack(fill=tk.BOTH, expand=True)
        map_editor_frame.pack()
        # --

        pained_window.add(non_map_editor_frame)
        pained_window.add(map_editor_frame)
        pained_window.pack(expand=True, fill=tk.BOTH)

    def run(self):
        self.setup()
        self.root.mainloop()

    def on_select_layer_type(self, event: tk.Event):
        if self.layer_type_strvar.get() == "trait":
            listbox: tk.Misc = event.widget
            self.trait_entry = tk.Entry(listbox.master, textvariable=self.traitbrush_strvar)
            self.trait_entry.pack()
        elif self.layer_type_strvar.get() == "terrain":
            if self.trait_entry:
                self.trait_entry.destroy()
                assert self.trait_entry is None
        print("unimplemented")

    def on_select_layer(self, event):
        print("unimplemented")

    def on_select_brush(self, event: tk.Event, preview_label: tk.Label):
        listbox: tk.Listbox = event.widget
        selection = listbox.curselection()
        if selection:
            self.current_brush = listbox.get(selection[0])
            image_bytes = Image.frombytes(
                "RGBA",
                (config.tile_width, config.tile_height),
                pygame.image.tobytes(tileid_to_surf[self.current_brush], "RGBA"),
            )
            image = ImageTk.PhotoImage(image_bytes)
            self.mapeditor_brushpreviewimage_buffer = image
            preview_label.configure(image=image)


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
