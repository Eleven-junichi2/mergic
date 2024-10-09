# TODO: make tests

from pathlib import Path
import os
from typing import Optional, TypeAlias
from pygame.math import Vector2
import pygame

EntityID: TypeAlias = int

FPS = 60

class AssetManager:
    def __init__(self):
        self.dict: dict[str, str | os.PathLike] = {}
    
    def register_asset(self, name: str, filepath: str | os.PathLike):
        self.dict[name] = filepath
    
    def load_img(self, name) -> pygame.Surface:
        return pygame.image.load(self.dict[name])

    def load_sound(self, name) -> pygame.mixer.Sound:
        return pygame.mixer.Sound(self.dict[name])

class GameMap:
    def __init__(self):
        self.data = {}

class Entity:
    def __init__(self, *components):
        self.components = components

class Hp:
    def __init__(self, max: int, initial_hp: Optional[int] = None):
        self.max = max
        self.value = initial_hp if initial_hp else max

class GameWorld:
    def __init__(self):
        self._next_entity_id = 0
        self.used_entity_ids: set[EntityID] = set()
        self.entities: dict[int, Entity] = {}
        self.maps: dict[str, GameMap] = {}
    
    def add_entity(self, entity) -> EntityID:
        self.entities[self._next_entity_id](entity)
        self.used_entity_ids.add(self._next_entity_id)
        entity_id = self._next_entity_id
        self._next_entity_id += 1
        return entity_id
    
    def set_gamemap(self, key, Level):
        self.maps[key] = Level

def main():
    pygame.init()

    world = GameWorld()
    player = world.add_entity(Entity(Hp(3)))

    clock = pygame.time.Clock()
    display = pygame.display.set_mode((640, 360))
    running = True
    dt = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        display.fill((0, 0, 0))
        pygame.display.flip()
        dt = clock.tick(FPS) # milliseconds
        print(dt)
    pygame.quit()


if __name__ == '__main__':
    main()
