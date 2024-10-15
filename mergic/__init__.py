from collections import OrderedDict, deque
from enum import Enum, auto
from typing import Any, Callable, Generator, Optional, Tuple, Type
from dataclasses import dataclass, field
from functools import partial
import os

import pygame
import pygame.freetype

entityclass = partial(dataclass, slots=True)


class AssetFinder:
    def __init__(self):
        self.dict: dict[str, str | os.PathLike] = {}

    def register(self, name: str, filepath: str | os.PathLike):
        self.dict[name] = filepath

    def load_img(self, name) -> pygame.Surface:
        return pygame.image.load(self.dict[name])

    def load_sound(self, name) -> pygame.mixer.Sound:
        return pygame.mixer.Sound(self.dict[name])

    def load_font(self, name) -> pygame.freetype.Font:
        return pygame.freetype.Font(self.dict[name])

    def filepath(self, name) -> str | os.PathLike:
        return self.dict[name]


class ImageAtlas:
    def __init__(
        self,
        image: pygame.Surface,
        atlases: dict[str, Tuple[Tuple[int, int], Tuple[int, int]]],
    ):
        self.image = image
        self.atlases = atlases

    @staticmethod
    def tile_atlases(
        self, tile_height, tile_width, row_count, column_count, how_many_tiles
    ):
        raise NotImplementedError

    def crop(self, atlas_name: str) -> pygame.Surface:
        if atlas_name not in self.atlases:
            raise ValueError("Invalid atlas name")
        return self.image.subsurface(
            self.atlases[atlas_name][0], self.atlases[atlas_name][1]
        )

    def name_to_surf_dict(self) -> dict[str, pygame.Surface]:
        return {atlas_name: self.crop(atlas_name) for atlas_name in self.atlases.keys()}


@dataclass
class GameMap[T]:
    # TODO: json serialization
    width: int
    height: int
    layers: dict[str, dict[str, T]] = field(default_factory=dict)

    def paint(self, layer: str, x: int, y: int, brush: T):
        if not isinstance(x, int) or not isinstance(y, int):
            raise ValueError("Coordinates must be integer values")
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            raise ValueError("Invalid coordinates")
        self.layers.setdefault(layer, {})
        self.layers[layer][f"{x},{y}"] = brush

    def erase_at(self, layer: str, x: int, y: int, raise_error_on_missing: bool = True):
        if not isinstance(x, int) or not isinstance(y, int):
            raise ValueError("Coordinates must be integer values")
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            raise ValueError("Invalid coordinates")
        try:
            del self.layers[layer][f"{x},{y}"]
        except KeyError:
            if raise_error_on_missing:
                raise ValueError(f"no element at ({x},{y})")

    def fetch_by_xy(self, x: int, y: int, layer: str):
        return self.layers[layer][f"{x},{y}"]

    def coordinates_of_elements(self, layer: str):
        yield from [
            [int(_) for _ in coordinate_str.split(",")]
            for coordinate_str in self.layers[layer].keys()
        ]

    def layer(self, layer_key: str):
        return self.layers[layer_key]

    def import_layer[T](self, layer_key: str, layer_data: dict[str, T]):
        self.layers[layer_key] = layer_data


class ECS:
    def __init__(self):
        self.entities: dict[type, list[object]] = {}
        self.dead_entity_buffer: list[object] = []
        self.maps: dict[str, GameMap] = {}

    def add(self, entity: object):
        self.entities.setdefault(entity.__class__, [])
        self.entities[entity.__class__].append(entity)

    def delete_now(self, entity):
        self.entities[entity.__class__].remove(entity)

    def reserve_to_delete(self, entity):
        self.dead_entity_buffer.append(entity)

    def do_reserved_deletions(self):
        for entity in self.dead_entity_buffer:
            self.delete_now(entity)
        self.dead_entity_buffer.clear()

    def entities_for_type[T](self, entity_type: Type[T]) -> Generator[T, Any, None]:
        yield from self.entities[entity_type]

    def entities_for_components[T](
        self, *component_types: type[T]
    ) -> Generator[T, Any, None]:
        # fix this to be more efficient
        for component_type in component_types:
            for entity_type in self.entities.keys():
                if component_type in entity_type.__mro__:
                    yield from self.entities_for_type(entity_type)


class ActionController:
    def __init__(self):
        self.actions: dict[
            str, dict[str, bool | Any]
        ] = {}  # example: { "action_key": {"active": False, "property": {}}}

    def add_action(self, action: str, property: dict):
        self.actions.setdefault(action, {"active": False, "property": property})

    def mutable_property(self, action: str):
        return self.actions[action]["property"]

    def do(self, action: str):
        if self.actions.get(action, False):
            self.actions[action]["active"] = True
        else:
            raise ValueError(f"Action '{action}' is not registered")

    def cancel(self, action: str):
        if self.actions.get(action, False):
            self.actions[action]["active"] = False
        else:
            raise ValueError(f"Action '{action}' is not registered")

    def is_active(self, action: str) -> bool:
        return self.actions[action]["active"]


class GameWorld(ECS):
    def __init__(self):
        super().__init__()
        self.maps: dict[str, GameMap] = {}

    def gamemap(self, map_name) -> GameMap:
        return self.maps.get(map_name)

    def set_gamemap(self, map_name, gamemap: GameMap):
        self.maps[map_name] = gamemap


@dataclass
class Scene:
    screen: pygame.surface.Surface
    manager: Optional["SceneManager"] = None

    @staticmethod
    def print_clockinfo(fn: Callable, measurement_times=3):
        fps_history = deque()

        def wrapper(self, dt):
            fps_history.append(1 / (dt / 1000) if dt != 0 else 0)
            fn(self, dt)
            print(
                f"delta time: {dt}, FPS(Average over {measurement_times} measurements): {sum(fps_history) / len(fps_history)}"
            )
            if len(fps_history) > measurement_times:
                fps_history.popleft()

        return wrapper

    def setup(self):
        pass

    def cleanup(self):
        pass

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, dt):
        pass

    def change_scene(self, next_scene_name: str):
        self.manager.change_scene(next_scene_name)


class SceneManager:
    def __init__(self):
        self.current_scene: Optional[str] = None
        self.scenes: dict[str, Scene] = {}

    def add(self, scene: Scene, scene_name=str):
        flag_to_setup = True if len(self.scenes) == 0 else False
        scene.manager = self
        self.scenes[scene_name] = scene
        if flag_to_setup:
            self.current_scene = scene_name
            self.scenes[self.current_scene].setup()

    def change_scene(self, next_scene_name: str):
        self.scenes[self.current_scene].cleanup()
        self.current_scene = next_scene_name
        self.scenes[self.current_scene].setup()

    def handle_event(self, event: pygame.event.Event):
        self.scenes[self.current_scene].handle_event(event)

    def update(self, dt):
        self.scenes[self.current_scene].update(dt)


class TextMenu:
    def __init__(self):
        self.options: OrderedDict[str, Callable] = OrderedDict()
        self.__longest_text_length: int = 0
        self.__selector: int = 0

    @property
    def longest_text_length(self) -> int:
        return self.__longest_text_length

    @property
    def selector(self) -> int:
        return self.__selector

    @selector.setter
    def selector(self, value: int):
        self.__selector = value

    def selector_up(self):
        self.selector = (self.selector - 1) % len(
            self.options
        )  # selector番号がoption数と一致すると余りなし=0となるので選択をループできる

    def selector_down(self):
        self.selector = (self.selector + 1) % len(self.options)

    def add_option(
        self, text: str, key: Optional[str] = None, callback: Optional[Callable] = None
    ):
        text_length = len(text)
        self.__longest_text_length = (
            text_length
            if text_length > self.longest_text_length
            else self.longest_text_length
        )
        if key is None:
            key = text
        self.options[key] = {"text": text, "callback": callback}

    def current_selection(self):
        return list(self.options.values())[self.selector]

    def execute_current_selection(self):
        return self.current_selection()["callback"]()


class MenuHighlightStyle(Enum):
    pass


class MenuCursorRenderPosition(Enum):
    LEFT = auto()
    RIGHT = auto()


class MenuCursor:
    def __init__(self):
        self.surface = None
        self.render_position = MenuCursorRenderPosition.RIGHT

    def set_surface(self, surface: pygame.surface.Surface):
        self.surface = surface

    def set_render_position(self, position: MenuCursorRenderPosition):
        self.render_position = position


class MenuUI:
    def __init__(self, menu: TextMenu, font: pygame.freetype.Font, cursor: Optional[MenuCursor] = None):
        self.menu = menu
        self.font = font
        self.cursor: Optional[MenuCursor] = cursor
        self.is_focused = False
        self.highlight_style: Optional[None] = None
        self.surface_cache: Optional[pygame.surface.Surface] = (
            None  # unused TODO: implement
        )

    def render(self) -> pygame.surface.Surface:
        cursor_width = 0
        if self.cursor:
            cursor_width = self.cursor.surface.get_width()
        entire_surface = pygame.surface.Surface(
            (
                self.font.size * self.menu.longest_text_length + cursor_width,
                self.font.size * len(self.menu.options),
            )
        )
        for i, option in enumerate(self.menu.options.values()):
            text_surface, text_rect = self.font.render(option["text"])
            text_x = 0
            text_y = i * text_rect.height
            if i == self.menu.selector and self.cursor:
                match self.cursor.render_position:
                    case MenuCursorRenderPosition.LEFT:
                        entire_surface.blit(self.cursor.surface, (text_x, text_y))
                        text_x = cursor_width
                    case MenuCursorRenderPosition.RIGHT:
                        entire_surface.blit(
                            self.cursor.surface, (text_rect.width, text_y)
                        )
            entire_surface.blit(
                text_surface,
                (text_x, text_y),
            )
        return entire_surface

    def update(self, dt):
        raise NotImplementedError
