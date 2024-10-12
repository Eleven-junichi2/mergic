# TODO: Refactoring

from collections import deque
import json
import os
import sys
from pathlib import Path
from tkinter import messagebox, ttk, simpledialog, filedialog
import tkinter as tk
from typing import Optional
from dataclasses import asdict, dataclass, field

from PIL import Image, ImageTk
import pygame

sys.path.append(str(Path(__file__).parent.parent.parent))

from mergic import GameMap, AssetFinder, ImageAtlas

CONFIG_FILEPATH = Path(__file__).parent / "config.json"


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
    tiletype_to_asset = json.load(f)


def clear_children(widget: tk.Misc):
    for widget in widget.winfo_children():
        widget.destroy()


@dataclass
class EditorVariables:
    layerlist: tk.StringVar = field(default_factory=tk.StringVar)
    layername_input: tk.StringVar = field(default_factory=tk.StringVar)
    tiletypelist: tk.StringVar = field(default_factory=tk.StringVar)
    current_layer: Optional[str] = None
    current_tilebrush: Optional[str] = None
    tile_selection_display_x: tk.StringVar = field(default_factory=tk.StringVar)
    tile_selection_display_y: tk.StringVar = field(default_factory=tk.StringVar)
    __rendered_tile_selector: deque[int] = field(
        default_factory=deque
    )  # use to clean map editor's canvas
    rendered_tile_img_references: deque[ImageTk.PhotoImage] = field(
        default_factory=deque
    )

    @property
    def rendered_tile_selector(self) -> deque[int]:
        return self.__rendered_tile_selector

    def delete_rendered_tile_selector(self, canvas: tk.Canvas):
        canvas.delete(*self.__rendered_tile_selector)
        self.__rendered_tile_selector.clear()

    def add_rendered_tile_selector(self, object_id: int):
        self.__rendered_tile_selector.append(object_id)


class App:
    def setup(self):
        self.gamemap: Optional[GameMap[str]] = None
        self.root = tk.Tk()
        self.root.title("GameMap Editor")
        self.root.geometry("640x360")
        self.editor_vars = EditorVariables()
        self.editor_frame = tk.Frame(self.root)

    def render_gamemap_on_canvas(
        self, canvas: tk.Canvas, layer_name: str, clear_before_draw: bool = False
    ):
        if self.gamemap:
            self.editor_vars.rendered_tile_img_references.clear()
            if clear_before_draw:
                canvas.delete(tk.ALL)
            canvas.create_rectangle(
                0,
                0,
                self.gamemap.width * config.tile_width,
                self.gamemap.height * config.tile_height,
                fill="black",
            )
            for x, y in self.gamemap.coordinates_of_elements(layer_name):
                tiletype = self.gamemap.fetch_by_xy(x, y, layer_name)
                tile_surf = tilesets[tiletype_to_asset[tiletype]["tileset"]].crop(
                    tiletype_to_asset[tiletype]["atlas"]
                )
                tile_size = tile_surf.get_size()
                image = ImageTk.PhotoImage(
                    Image.frombytes(
                        "RGBA", tile_size, pygame.image.tobytes(tile_surf, "RGBA")
                    )
                )
                self.editor_vars.rendered_tile_img_references.append(image)
                canvas.create_image(
                    x * config.tile_width + config.tile_width // 2,
                    y * config.tile_height + config.tile_height // 2,
                    image=image,
                )

    def render_tile_selector(
        self, canvas: tk.Canvas, mouse_x, mouse_y, clear_before_draw: bool = False
    ):
        if clear_before_draw:
            canvas.delete(tk.ALL)
        tile_x = canvas.canvasx(mouse_x) // config.tile_width
        tile_y = canvas.canvasy(mouse_y) // config.tile_height
        self.editor_vars.tile_selection_display_x.set(f"x={tile_x}")
        self.editor_vars.tile_selection_display_y.set(f"y={tile_y}")
        id = canvas.create_rectangle(
            tile_x * config.tile_width,
            tile_y * config.tile_height,
            tile_x * config.tile_width + config.tile_width,
            tile_y * config.tile_height + config.tile_height,
            outline="yellow",
        )
        self.editor_vars.add_rendered_tile_selector(id)

    def on_mouse_enter_canvas(self, event: tk.Event):
        canvas: tk.Canvas = event.widget
        if layer := self.editor_vars.current_layer:
            self.render_gamemap_on_canvas(canvas, layer, clear_before_draw=True)
        self.editor_vars.delete_rendered_tile_selector(canvas)
        self.render_tile_selector(event.widget, event.x, event.y)

    def on_leftclick_canvas(self, event: tk.Event):
        canvas: tk.Canvas = event.widget
        self.paint_tile_on_canvas_with_mouse(canvas, event.x, event.y)

    def on_rightclick_canvas(self, event: tk.Event):
        canvas: tk.Canvas = event.widget
        self.erase_tile_on_canvas_with_mouse(canvas, event.x, event.y)

    def paint_tile_on_canvas_with_mouse(
        self, canvas: tk.Canvas, mouse_x: int, mouse_y: int
    ):
        if self.editor_vars.current_tilebrush is None:
            return
        tile_x = canvas.canvasx(mouse_x) // config.tile_width
        tile_y = canvas.canvasy(mouse_y) // config.tile_height
        if layer_key := self.editor_vars.current_layer:
            self.gamemap.paint(
                layer_key,
                round(tile_x),
                round(tile_y),
                self.editor_vars.current_tilebrush,
            )
            self.render_gamemap_on_canvas(canvas, layer_key)

    def erase_tile_on_canvas_with_mouse(
        self, canvas: tk.Canvas, mouse_x: int, mouse_y: int
    ):
        tile_x = canvas.canvasx(mouse_x) // config.tile_width
        tile_y = canvas.canvasy(mouse_y) // config.tile_height
        if layer_key := self.editor_vars.current_layer:
            self.gamemap.erase_at(
                layer_key, round(tile_x), round(tile_y), raise_error_on_missing=False
            )
            self.render_gamemap_on_canvas(canvas, layer_key)

    def reconstruct_mapeditor_window(self) -> tk.Canvas:
        mapeditor_window = tk.Toplevel()
        mapeditor_window.title("Map Editor")
        mapeditor_window.geometry("320x320")

        mapcanvas = tk.Canvas(mapeditor_window)
        mapcanvas.pack(fill=tk.BOTH, expand=True)
        mapcanvas.bind("<Motion>", self.on_mouse_enter_canvas)
        mapcanvas.bind("<Button-1>", self.on_leftclick_canvas)
        mapcanvas.bind("<Button-3>", self.on_rightclick_canvas)
        vscrollbar = tk.Scrollbar(
            mapcanvas, orient=tk.VERTICAL, command=mapcanvas.yview
        )
        mapcanvas.configure(scrollregion=(0, 0, 900, 900))
        mapcanvas.configure(yscrollcommand=vscrollbar.set)
        vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        separator_horizontal = ttk.Separator(mapeditor_window, orient=tk.HORIZONTAL)
        separator_horizontal.pack(fill=tk.X)

        selected_tile_display_x = tk.Label(
            mapeditor_window, textvariable=self.editor_vars.tile_selection_display_x
        )
        selected_tile_display_x.pack()
        selected_tile_display_y = tk.Label(
            mapeditor_window, textvariable=self.editor_vars.tile_selection_display_y
        )
        selected_tile_display_y.pack()
        return mapcanvas

    def reconstruct_editor(self):
        clear_children(self.editor_frame)
        self.editor_vars = EditorVariables()
        self.update_layerlist()
        self.update_tiletypelist()

        # --マップ編集画面--
        mapcanvas = self.reconstruct_mapeditor_window()
        # --

        separator_horizontal = ttk.Separator(self.editor_frame, orient=tk.HORIZONTAL)
        separator_horizontal.pack(fill=tk.X)

        # --レイヤー編集画面
        layers_frame = tk.Frame(self.editor_frame)
        tk.Label(layers_frame, text="Layers").pack()
        layer_listbox = tk.Listbox(
            layers_frame,
            selectmode=tk.SINGLE,
            listvariable=self.editor_vars.layerlist,
        )
        layer_listbox.bind(
            "<<ListboxSelect>>", lambda event: self.on_select_layer(event, mapcanvas)
        )
        layername_input = tk.Entry(
            layers_frame, textvariable=self.editor_vars.layername_input
        )
        layer_listbox.pack()
        layername_input.pack()
        add_layer_btn = tk.Button(
            layers_frame, text="Add Layer", command=self.add_layer
        )
        add_layer_btn.pack()
        layers_frame.pack(side=tk.LEFT)
        # --

        # --tile pallate
        pallete_frame = tk.Frame(self.editor_frame)
        tk.Label(pallete_frame, text="Pallete").pack()
        tile_preview_widget = tk.Label(pallete_frame)
        tiletype_listbox = tk.Listbox(
            pallete_frame,
            selectmode=tk.SINGLE,
            listvariable=self.editor_vars.tiletypelist,
        )
        tiletype_listbox.bind(
            "<<ListboxSelect>>",
            lambda event: self.on_select_tilebrush(event, tile_preview_widget),
        )
        tile_preview_widget.pack()
        tiletype_listbox.pack()
        pallete_frame.pack()
        # --

        separator_horizontal = ttk.Separator(self.editor_frame, orient=tk.HORIZONTAL)
        separator_horizontal.pack(fill=tk.X)

        # --display GameMap info
        gamemap_info_frame = tk.Frame(self.editor_frame)
        width_display = tk.Label(
            gamemap_info_frame, text=f"width: {self.gamemap.width}"
        )
        height_display = tk.Label(
            gamemap_info_frame, text=f"height: {self.gamemap.height}"
        )
        width_display.pack(side=tk.LEFT)
        height_display.pack(side=tk.LEFT)
        gamemap_info_frame.pack()
        # --
        self.editor_frame.pack()

    def run(self):
        self.setup()
        # --メニューバー
        menubar = tk.Menu(self.root)
        self.root.configure(menu=menubar)
        filemenu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New", command=self.new_gamemap_dialog)
        filemenu.add_separator()
        filemenu.add_command(label="Save As", command=self.save_as_gamemap_dialog)
        filemenu.add_separator()
        filemenu.add_command(label="Open", command=self.open_gamemap_dialog)
        menubar.add_cascade(label="Config")
        # --
        self.root.mainloop()

    def update_layerlist(self):
        self.editor_vars.layerlist.set(list(self.gamemap.layers.keys()))

    def update_tiletypelist(self):
        self.editor_vars.tiletypelist.set(list(tiletype_to_asset.keys()))

    def add_layer(self):
        layername = self.editor_vars.layername_input.get()
        self.gamemap.import_layer(layername, {})
        self.update_layerlist()

    def on_select_tilebrush(self, event: tk.Event, tile_preview_widget: tk.Label):
        listbox: tk.Listbox = event.widget
        selection = listbox.curselection()
        if selection:
            self.editor_vars.current_tilebrush = listbox.get(selection)
            tiletype = self.editor_vars.current_tilebrush
            tile_surf = tilesets[tiletype_to_asset[tiletype]["tileset"]].crop(
                tiletype_to_asset[tiletype]["atlas"]
            )
            image = ImageTk.PhotoImage(
                Image.frombytes(
                    "RGBA",
                    tile_surf.get_size(),
                    pygame.image.tobytes(tile_surf, "RGBA"),
                )
            )
            tile_preview_widget.image = image  # to avoid garbage collection
            tile_preview_widget.configure(image=image)
            tile_preview_widget.update()

    def on_select_layer(self, event: tk.Event, canvas: tk.Canvas):
        listbox: tk.Listbox = event.widget
        selection = listbox.curselection()
        if selection:
            self.editor_vars.current_layer = listbox.get(selection[0])
            if not canvas.winfo_exists():
                canvas = self.reconstruct_mapeditor_window()
                listbox.bind(
                    "<<ListboxSelect>>",
                    lambda event: self.on_select_layer(event, canvas),
                )
            self.render_gamemap_on_canvas(canvas, self.editor_vars.current_layer)

    def save_as_gamemap_dialog(self):
        if self.gamemap is None:
            messagebox.showerror(None, "Nothing to save.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("GameMap(.json)", "*.json"), ("All files", "*.*")],
        )
        if filepath:
            with open(filepath, "w") as f:
                json.dump(asdict(self.gamemap), f)
                messagebox.showinfo(None, "GameMap was saved successfully.")

    def load_gamemap_from_file(self, filepath: str | os.PathLike):
        with open(filepath, "r") as f:
            gamemap = json.load(f)
            self.gamemap = GameMap[str](
                gamemap["width"], gamemap["height"], layers=gamemap["layers"]
            )
        self.update_layerlist()
        self.reconstruct_editor()

    def open_gamemap_dialog(self):
        filepath = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("GameMap(.json)", "*.json"), ("All files", "*.*")],
        )
        if filepath:
            self.load_gamemap_from_file(filepath)

    def new_gamemap_dialog(self):
        width = simpledialog.askinteger("New GameMap", "Enter width:", initialvalue=3)
        height = simpledialog.askinteger("New GameMap", "Enter height:", initialvalue=3)
        if width is None or height is None:
            return
        self.gamemap = GameMap[str](width=width, height=height)
        self.reconstruct_editor()


if __name__ == "__main__":
    app = App()
    app.run()
