from collections import deque
import os
from typing import Any, Callable, Generator, Optional, Tuple, Type
from dataclasses import dataclass, field
from functools import partial

import pygame

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
    def tile_atlases(self, tile_height, tile_width, row_count, column_count, how_many_tiles):
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
        
        # if layer in self.layers and f"{x},{y}" in self.layers[layer]:
        #     del self.layers[layer][f"{x},{y}"]
    
    def fetch_by_xy(self, x: int, y: int, layer: str):
        return self.layers[layer][f"{x},{y}"]

    def coordinates_of_elements(self, layer: str):
        yield from [[int(_) for _ in coordinate_str.split(",")] for coordinate_str in self.layers[layer].keys()]

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

    def entities_for_components(self, *component_types: type):
        # fix this to be more efficient
        for component_type in component_types:
            for entity_type in self.entities.keys():
                if component_type in entity_type.__mro__:
                    yield from self.entities_for_type(entity_type)


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
            print(f"delta time: {dt}, FPS(Average over {measurement_times} measurements): {sum(fps_history) / len(fps_history)}")
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
        # print("scene: ", self.current_scene)
