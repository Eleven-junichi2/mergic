import os
from typing import Any, Generator, Tuple, Type
from dataclasses import dataclass
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

class ImageAtlas:
    def __init__(self, image: pygame.Surface, atlases: dict[str, ((int, int), (int, int))]):
        self.image = image
        self.atlases = atlases
    
    def crop(self, atlas: str) -> pygame.Surface:
        if atlas not in self.atlases:
            raise ValueError("Invalid atlas name")
        return self.image.subsurface(self.atlases[atlas][0], self.atlases[atlas][1])


class GameMap[T]:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.layers: dict[str, dict[Tuple[int, int], T]] = {}

    def paint(self, layer: str, x: int, y: int, brush: T):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            raise ValueError("Invalid coordinates")
        self.layers.setdefault(layer, {})
        self.layers[layer][(x, y)] = brush

    def layer(self, layer_key: str):
        return self.layers[layer_key]

    def import_layer(self, layer_key: str, layer_data: dict[Tuple[int, int], T]):
        self.layers[layer_key] = layer_data

    # def export_as_2d_list(self) -> tuple[tuple[Any]]:
    #     list2d = [_ for _ in ]


class ECS:
    def __init__(self):
        self.entities: dict[type, list[object]] = {}
        # self.entity_components: dict[type, tuple[object]] = {}
        self.dead_entity_buffer: list[object] = []
        self.maps: dict[str, GameMap] = {}

    def add(self, entity: object):
        self.entities.setdefault(entity.__class__, [])
        # self.entity_components.setdefault(entity.__class__, entity.__class__.__mro__)
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

    
    def gamemap(self, map_name) -> GameMap:\
        return self.maps.get(map_name)

    def set_gamemap(self, map_name, gamemap: GameMap):
        self.maps[map_name] = gamemap
