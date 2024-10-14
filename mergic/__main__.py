# TODO: make tests
from collections import deque
from pathlib import Path
import tomllib
import json
from typing import Iterable, Tuple

import pygame
from pygame.event import Event
from pygame.math import Vector2

from mergic.components import PygameSurface

from . import GameWorld, AssetFinder, GameMap, ImageAtlas, SceneManager, Scene
from .calculation_tools import calc_center_pos
from .entities import Player


FPS = 60

ASSETS_DIR = Path(__file__).parent / "assets"

asset_finder = AssetFinder()
asset_finder.register("title", ASSETS_DIR / "imgs" / "title.png")


def load_config():
    with open(Path(__file__).parent / "config.toml", "r") as f:
        return tomllib.load(f)


def load_localized_texts(language_code="en"):
    with open(Path(__file__).parent / "i18n" / f"{language_code}.json", "r") as f:
        return json.load(f)


class TitleScene(Scene):
    def setup(self):
        self.title_surface = asset_finder.load_img("title")
        self.flag_gamescene = False
    
    def handle_event(self, event: Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.flag_gamescene = True

    @Scene.print_clockinfo
    def update(self, dt):
        if self.flag_gamescene:
            self.change_scene("game")
        self.screen.blit(
            self.title_surface,
            calc_center_pos(self.title_surface.get_size(), self.screen.get_size()),
        )

class GameScene(Scene):
    def setup(self):
        self.world = GameWorld()
        player_surf = pygame.Surface((16, 16))
        player_surf.fill(pygame.Color("red"))
        player = Player(pos=Vector2(0, 0), surface=player_surf, vel=Vector2(0, 0))
        self.world.add(player)

    def update(self, dt):
        self.screen.fill((0, 0, 0))
        scancode_map = pygame.key.get_pressed()
        for player in self.world.entities_for_type(Player):
            player.vel.y = 2 * (scancode_map[pygame.K_DOWN] - scancode_map[pygame.K_UP])
            player.vel.x = 2 * (scancode_map[pygame.K_RIGHT] - scancode_map[pygame.K_LEFT])
            player.pos += player.vel * dt / 1000
            self.screen.blit(player.surface, player.pos)


def main():
    pygame.init()
    clock = pygame.time.Clock()
    screen_size = [640, 360]
    px_scale = 2
    display = pygame.display.set_mode(screen_size)
    screen = pygame.surface.Surface([size // px_scale for size in screen_size])
    scene_manager = SceneManager()
    scene_manager.add(TitleScene(screen), "title")
    scene_manager.add(GameScene(screen), "game")
    running = True
    dt = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            scene_manager.handle_event(event)
        scene_manager.update(dt)
        pygame.transform.scale(
            screen, screen_size, display
        )  # 3rd argument does display.blit()
        pygame.display.flip()
        dt = clock.tick(FPS)  # milliseconds
    pygame.quit()


if __name__ == "__main__":
    main()
