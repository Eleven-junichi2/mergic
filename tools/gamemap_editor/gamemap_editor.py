# TODO: Refactor code

from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Optional
from tkinter import filedialog, messagebox, simpledialog
import tkinter as tk
import json
import sys
import os

from PIL import Image, ImageTk
import pygame

sys.path.append(str(Path(__file__).parent.parent.parent))

from mergic import GameMap, AssetFinder, ImageAtlas

CONFIG_FILEPATH = Path(__file__).parent / "config.json"


# --initialization
@dataclass
class Config:
    tile_width: int = 16
    tile_height: int = 16
    tileset_dirpath: str | os.PathLike = str(
        Path(__file__).parent.parent.parent / "mergic" / "assets" / "imgs" / "tilesets"
    )
    tiletype_to_asset_filepath: str | os.PathLike = str(
        Path(__file__).parent / "tiletype_to_asset.json"
    )


if not CONFIG_FILEPATH.exists():
    config = Config()
    with open(CONFIG_FILEPATH, "w") as f:
        json.dump(asdict(config), f, indent=4)
else:
    with open(CONFIG_FILEPATH, "r", encoding="utf-8") as f:
        config = Config(**json.load(f))

assets = AssetFinder()
tilesets: dict[str, ImageAtlas] = {}
for filepath in Path(config.tileset_dirpath).iterdir():
    if filepath.is_file() and filepath.suffix == ".png":
        assets.register(filepath.stem, filepath)
        with open(filepath.with_suffix(".json"), "r") as f:
            atlases = json.load(f)
        tilesets[filepath.stem] = ImageAtlas(
            assets.load_img(filepath.stem),
            atlases,
        )

if not Path(config.tiletype_to_asset_filepath).exists():
    messagebox.showerror(
        "Error",
        f"Could not find '{Path(config.tiletype_to_asset_filepath).name}'. Please make sure it exists in '{Path(config.tiletype_to_asset_filepath).parent}'",
    )
with open(config.tiletype_to_asset_filepath, "r", encoding="utf-8") as f:
    tiletype_to_assetinfo: dict[str, dict[str, str]] = json.load(f)
    tiletype_to_surf: dict[str, pygame.Surface] = {}
    for tiletype, assetinfo in tiletype_to_assetinfo.items():
        tiletype_to_surf[tiletype] = tilesets[assetinfo["tileset"]].crop(
            assetinfo["atlas"]
        )
# --


class GameMapEditor:
    def __init__(
        self,
        gamemap: Optional[GameMap] = None,
        on_mutate_layers_via_editor: Optional[Callable] = None,
    ):
        self.gamemap_buffer: Optional[GameMap] = gamemap
        self.on_mutate_layers_via_editor: Optional[Callable] = (
            on_mutate_layers_via_editor
        )
        self.__current_layer_selection: Optional[str] = None

    def add_new_layer(self, layer_name):
        self.gamemap_buffer.import_layer(layer_name, {})
        if func:= self.on_mutate_layers_via_editor:
            func()

    def import_gamemap_from_file(self, filepath: str | os.PathLike):
        with open(filepath, "r") as f:
            gamemap = json.load(f)
            self.gamemap_buffer = GameMap(
                gamemap["width"], gamemap["height"], layers=gamemap["layers"]
            )
        if func := self.on_mutate_layers_via_editor:
            func()
            

    def save_gamemap_as_file(self, filepath: str | os.PathLike):
        with open(filepath, "w") as f:
            json.dump(asdict(self.gamemap_buffer), f, indent=4)

    def display_layerlist(self):
        return list(self.gamemap_buffer.layers.keys())

    def select_layer(self, layer: str):
        self.__current_layer_selection = layer

    def current_layer_selection(self) -> str:
        return self.__current_layer_selection

    def display_layer(self):
        map_surf = pygame.Surface(
            size=(
                self.gamemap_buffer.width * config.tile_width,
                self.gamemap_buffer.height * config.tile_height,
            )
        )
        for coordinate_str, tiletype in self.gamemap_buffer.layer(
            self.current_layer_selection()
        ).items():
            x, y = coordinate_str.split(",")
            x = int(x)
            y = int(y)
            map_surf.blit(
                tiletype_to_surf[tiletype],
                (x * config.tile_width, y * config.tile_height),
            )
        return pygame.image.tobytes(map_surf, "RGBA")


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mergic GameMap Editor")
        self.root.geometry("640x540")
        self.gamemap_editor: GameMapEditor = None
        self.mapeditor_canvasimage_buffer = None
        self.mapeditor_tileselector_canvasobject_ids = deque()
        self.mapeditor_gamemapimage_canvasobject_ids = deque()
        self.brush_list_var = tk.StringVar()
        self.brush_list_var.set(list(tiletype_to_surf.keys()))
        self.current_brush: Optional[str] = None
        self.layer_name_input_var = tk.StringVar()
        self.layerlist_buffer = tk.StringVar()

    def reset_gamemap_editor(self, gamemap: Optional[GameMap] =None):
        self.gamemap_editor = GameMapEditor(
            gamemap=gamemap,
            on_mutate_layers_via_editor=lambda: self.layerlist_buffer.set(
                self.gamemap_editor.display_layerlist()
            )
        )

    def dialog_openfile(self):
        filepath = filedialog.askopenfilename(
            defaultextension=".json", filetypes=[("GameMap(.json)", "*.json")]
        )
        if filepath:
            self.reset_gamemap_editor()
            self.gamemap_editor.import_gamemap_from_file(filepath)

    def dialog_savefile(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("GameMap(.json)", "*.json")]
        )
        if filepath:
            self.gamemap_editor.save_gamemap_as_file()

    def on_select_layer(self, event: tk.Event, canvas: tk.Canvas):
        listbox: tk.Listbox = event.widget
        selection = listbox.curselection()
        if selection:
            self.gamemap_editor.select_layer(listbox.get(selection[0]))
            self.render_gamemap_on_canvas(canvas)

    def render_gamemap_on_canvas(self, canvas: tk.Canvas):
        canvas.delete(*self.mapeditor_gamemapimage_canvasobject_ids)
        self.mapeditor_gamemapimage_canvasobject_ids.clear()
        map_image_bytes = self.gamemap_editor.display_layer()
        image = ImageTk.PhotoImage(
            Image.frombytes(
                "RGBA",
                (
                    config.tile_width * self.gamemap_editor.gamemap_buffer.width,
                    config.tile_height * self.gamemap_editor.gamemap_buffer.height,
                ),
                map_image_bytes,
            )
        )
        self.mapeditor_canvasimage_buffer = image
        # set half size of image for coordinates
        # because create_image calc image's coordinates from center of image
        # ↓
        id = canvas.create_image(
            image.width() // 2,
            image.height() // 2,
            image=image,
        )
        self.mapeditor_gamemapimage_canvasobject_ids.append(id)

    def on_mouse_in_canvas(self, event: tk.Event):
        canvas: tk.Canvas = event.widget
        self.render_tile_selector(canvas, event.x, event.y)

    def on_leftclick_canvas(self, event: tk.Event):
        canvas: tk.Canvas = event.widget
        self.paint_tile_on_canvas_with_mouse(canvas, event.x, event.y)

    def on_rightclick_canvas(self, event: tk.Event):
        canvas: tk.Canvas = event.widget
        self.erase_tile_on_canvas_with_mouse(canvas, event.x, event.y)

    def paint_tile_on_canvas_with_mouse(
        self, canvas: tk.Canvas, mouse_x: int, mouse_y: int
    ):
        if self.current_brush is None:
            return
        tile_x = canvas.canvasx(mouse_x) // config.tile_width
        tile_y = canvas.canvasy(mouse_y) // config.tile_height
        if layer_key := self.gamemap_editor.current_layer_selection():
            self.gamemap_editor.gamemap_buffer.paint(
                layer_key,
                round(tile_x),
                round(tile_y),
                self.current_brush,
            )
            self.render_gamemap_on_canvas(canvas)

    def erase_tile_on_canvas_with_mouse(
        self, canvas: tk.Canvas, mouse_x: int, mouse_y: int
    ):
        tile_x = canvas.canvasx(mouse_x) // config.tile_width
        tile_y = canvas.canvasy(mouse_y) // config.tile_height
        if layer_key := self.gamemap_editor.current_layer_selection():
            self.gamemap_editor.gamemap_buffer.erase_at(
                layer_key, round(tile_x), round(tile_y), raise_error_on_missing=False
            )
            self.render_gamemap_on_canvas(canvas)

    def render_tile_selector(self, canvas: tk.Canvas, mouse_x, mouse_y):
        canvas.delete(*self.mapeditor_tileselector_canvasobject_ids)
        self.mapeditor_tileselector_canvasobject_ids.clear()
        tile_x = canvas.canvasx(mouse_x) // config.tile_width
        tile_y = canvas.canvasy(mouse_y) // config.tile_height
        # print(f"x={tile_x},y={tile_y}")
        id = canvas.create_rectangle(
            tile_x * config.tile_width,
            tile_y * config.tile_height,
            tile_x * config.tile_width + config.tile_width,
            tile_y * config.tile_height + config.tile_height,
            outline="yellow",
        )
        self.mapeditor_tileselector_canvasobject_ids.append(id)

    def on_select_brush(self, event: tk.Event, preview_widget: tk.Label):
        listbox: tk.Listbox = event.widget
        selection = listbox.curselection()
        if selection:
            self.current_brush = listbox.get(selection[0])
            image_bytes = Image.frombytes(
                "RGBA",
                (config.tile_width, config.tile_height),
                pygame.image.tobytes(tiletype_to_surf[self.current_brush], "RGBA"),
            )
            image = ImageTk.PhotoImage(image_bytes)
            self.mapeditor_brushpreviewimage_buffer = image
            preview_widget.configure(image=image)

    def dialog_new_gamemap(self):
        width = simpledialog.askinteger(None, "tile width", initialvalue=9)
        if width is None:
            return
        height = simpledialog.askinteger(None, "tile height", initialvalue=9)
        if height is None:
            return
        self.reset_gamemap_editor(GameMap(width=width, height=height))
        self.gamemap_editor.on_mutate_layers_via_editor()

    def on_btn_add_layer(self):
        self.gamemap_editor.add_new_layer(self.layer_name_input_var.get())

    def setup(self):
        menubar = tk.Menu(self.root)
        self.root.configure(menu=menubar)
        menu_file = tk.Menu(menubar)
        menu_file.add_cascade(label="New", command=self.dialog_new_gamemap)
        menu_file.add_cascade(label="Save", command=self.dialog_savefile)
        menu_file.add_cascade(label="Open", command=self.dialog_openfile)
        menubar.add_cascade(label="File", menu=menu_file)

        pained_window = tk.PanedWindow(self.root, sashwidth=4, sashrelief=tk.SOLID)

        non_mapeditor_area = tk.Frame(self.root)
        # pallete
        pallate_frame = tk.Frame(non_mapeditor_area, bd=1, relief=tk.RAISED)
        brush_list = tk.Listbox(
            pallate_frame, selectmode=tk.SINGLE, listvariable=self.brush_list_var
        )
        tk.Label(pallate_frame, text="Pallate").pack()
        preview_widget = tk.Label(pallate_frame)
        brush_list.bind(
            "<<ListboxSelect>>",
            lambda event: self.on_select_brush(event, preview_widget),
        )
        preview_widget.pack()
        brush_list.pack()
        pallate_frame.pack(pady=2)
        # layer editor
        layer_editor_frame = tk.Frame(non_mapeditor_area, bd=1, relief=tk.RAISED)
        tk.Label(layer_editor_frame, text="Layers").pack()
        layer_list = tk.Listbox(
            layer_editor_frame, selectmode=tk.SINGLE, listvariable=self.layerlist_buffer
        )

        # prepare mapeditor canvas
        map_editor_frame = tk.Frame(self.root, bd=1)
        map_editor_canvas = tk.Canvas(map_editor_frame)
        # --

        layer_list.bind(
            "<<ListboxSelect>>",
            lambda event: self.on_select_layer(event, map_editor_canvas),
        )
        # self.gamemap_editor.on_import_gamemap = lambda gamemap: layerlist_buffer.set(
        #     self.gamemap_editor.display_layerlist()
        # )
        btns_to_edit_layer_name_frame = tk.Frame(layer_editor_frame)
        btn_rename_layer = tk.Button(btns_to_edit_layer_name_frame, text="Rename")
        entry_layer_name = tk.Entry(
            layer_editor_frame, textvariable=self.layer_name_input_var
        )
        btn_add_layer = tk.Button(
            btns_to_edit_layer_name_frame,
            text="Add",
            command=self.on_btn_add_layer,
        )
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

        # -- map editor canvas

        map_editor_canvas.bind("<Motion>", self.on_mouse_in_canvas)
        map_editor_canvas.bind("<Button-1>", self.on_leftclick_canvas)
        map_editor_canvas.bind("<Button-3>", self.on_rightclick_canvas)
        vertical_scrollbar = tk.Scrollbar(
            map_editor_canvas, orient=tk.VERTICAL, command=map_editor_canvas.yview
        )
        horizontal_scrollbar = tk.Scrollbar(
            map_editor_canvas, orient=tk.HORIZONTAL, command=map_editor_canvas.xview
        )
        map_editor_canvas.configure(scrollregion=(0, 0, 900, 900))
        map_editor_canvas.configure(yscrollcommand=vertical_scrollbar.set)
        map_editor_canvas.configure(xscrollcommand=horizontal_scrollbar.set)
        vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        map_editor_canvas.pack(fill=tk.BOTH, expand=True)
        map_editor_frame.pack(side=tk.RIGHT)

        pained_window.add(non_mapeditor_area)
        pained_window.add(map_editor_frame)
        pained_window.pack(expand=True, fill=tk.BOTH)

    def run(self):
        self.setup()
        self.root.mainloop()
