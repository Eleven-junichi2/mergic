# TODO: Refactoring

import json
import os
from pathlib import Path
from tkinter import messagebox, ttk, simpledialog, filedialog
import tkinter as tk
from typing import Optional
from dataclasses import asdict, dataclass, field

from . import GameMap, AssetFinder, ImageAtlas

assets = AssetFinder()
assets.register(
    "tileset", Path(__file__).parent / "assets" / "imgs" / "terrain" / "Grass.png"
)
tileset = ImageAtlas(
    assets.load_img("tileset"),
    {"water": ((0, 0), (16, 16)), "grass": ((16, 0), (16, 16))},
)

tiletype_to_surface = tileset.name_to_surf_dict()


@dataclass
class Config:
    tile_width: int = 16
    tile_height: int = 16


config = Config()


def clear_children(widget: tk.Misc):
    for widget in widget.winfo_children():
        widget.destroy()


@dataclass
class EditorVariables:
    layerlist: tk.StringVar = field(default_factory=tk.StringVar)
    layername_input: tk.StringVar = field(default_factory=tk.StringVar)
    current_layer: Optional[str] = None


class App:
    def setup(self):
        self.gamemap: Optional[GameMap] = None
        self.root = tk.Tk()
        self.root.title("GameMap Editor")
        self.root.geometry("640x360")
        self.editor_vars = EditorVariables()
        self.editor_frame = tk.Frame(self.root)

    def render_gamemap_on_canvas(self, canvas: tk.Canvas, layer_name: str):
        if self.gamemap:
            canvas.create_rectangle(
                0,
                0,
                self.gamemap.width * config.tile_width,
                self.gamemap.height * config.tile_height,
                fill="black",
            )
            for x, y in self.gamemap.coordinates_of_elements(layer_name):
                canvas.create_rectangle(
                    x * config.tile_width,
                    y * config.tile_width,
                    x * config.tile_width + config.tile_width,
                    y * config.tile_height + config.tile_height,
                    fill="green",
                )
            # canvas.update()

    def render_tile_selector(self, canvas: tk.Canvas, mouse_x, mouse_y):
        tile_x = mouse_x // config.tile_width
        tile_y = mouse_y // config.tile_height
        print("x, y", tile_x, tile_y)
        canvas.create_rectangle(
            tile_x * config.tile_width,
            tile_y * config.tile_height,
            tile_x * config.tile_width + config.tile_width,
            tile_y * config.tile_height + config.tile_height,
            outline="yellow",
        )

    def on_mouse_enter_canvas(self, event: tk.Event):
        self.render_gamemap_on_canvas(event.widget, self.editor_vars.current_layer)
        self.render_tile_selector(event.widget, event.x, event.y)


    def reconstruct_editor(self):
        clear_children(self.editor_frame)

        mapcanvas = tk.Canvas(self.editor_frame)
        mapcanvas.pack(fill=tk.BOTH, expand=True)
        mapcanvas.bind("<Motion>", self.on_mouse_enter_canvas)

        separator_horizontal = ttk.Separator(self.editor_frame, orient=tk.HORIZONTAL)
        separator_horizontal.pack(fill=tk.X)

        # --レイヤー編集画面
        layer_selection = tk.Listbox(
            self.editor_frame,
            selectmode=tk.SINGLE,
            listvariable=self.editor_vars.layerlist,
        )
        layer_selection.bind(
            "<<ListboxSelect>>", lambda event: self.on_select_layer(event, mapcanvas)
        )
        layername_input = tk.Entry(
            self.editor_frame, textvariable=self.editor_vars.layername_input
        )
        layer_selection.pack()
        layername_input.pack()
        add_layer_btn = tk.Button(
            self.editor_frame, text="Add Layer", command=self.add_layer
        )
        add_layer_btn.pack()
        # --

        separator_horizontal = ttk.Separator(self.editor_frame, orient=tk.HORIZONTAL)
        separator_horizontal.pack(fill=tk.X)

        # --display GameMap info
        width_display = tk.Label(self.editor_frame, text=f"width: {self.gamemap.width}")
        height_display = tk.Label(
            self.editor_frame, text=f"height: {self.gamemap.height}"
        )
        width_display.pack()
        height_display.pack()
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

    def add_layer(self):
        layername = self.editor_vars.layername_input.get()
        self.gamemap.import_layer(layername, {})
        self.update_layerlist()

    def on_select_layer(self, event: tk.Event, canvas: tk.Canvas):
        listbox: tk.Listbox = event.widget
        selection = listbox.curselection()
        if selection:
            print(listbox.get(selection[0]))
            self.editor_vars.current_layer = listbox.get(selection[0])
            self.render_gamemap_on_canvas(canvas, listbox.get(selection[0]))

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
            self.gamemap = GameMap(
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
        self.gamemap = GameMap(width=width, height=height)
        self.update_layerlist()
        self.reconstruct_editor()


if __name__ == "__main__":
    app = App()
    app.run()
