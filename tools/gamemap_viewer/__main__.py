from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path

import pygame
from mergic.asset import AssetFinder, ImageAtlas
from mergic.gamemap import (
    TileMap,
    register_imgs_and_existing_regions_files_in_dirs,
    build_tileid_to_surf_from_img_dirs,
)

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


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tile Map Viewer")
        self.root.geometry("640x540")
        self.brush_listvar = tk.StringVar()
        self.brush_listvar.set(list(tileid_to_surf.keys()))

    def setup(self):
        pallate_frame = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        brush_list = tk.Listbox(
            pallate_frame, selectmode=tk.SINGLE, listvariable=self.brush_listvar
        )
        tk.Label(pallate_frame, text="Pallate").pack()
        preview_widget = tk.Label(pallate_frame)
        brush_list.bind(
            "<<ListboxSelect>>",
            lambda event: self.on_select_brush(event, preview_widget),
        )
        preview_widget.pack()
        brush_list.pack(expand=True)
        pallate_frame.pack()

    def run(self):
        self.setup()
        self.root.mainloop()

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
