# TODO: make tests
from pathlib import Path
import tomllib
import json
from typing import Iterable, Tuple

import pygame

from . import GameWorld, AssetFinder, GameMap, ImageAtlas, SceneManager, Scene


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

def calc_center_pos(target_size: Iterable[int], canvas_size: Iterable[int]) -> list[int, int]:
    """Calculate position of `target` to center it on the `canvas`"""
    return [csize // 2 - tsize // 2 for tsize, csize in zip(target_size, canvas_size)]


class TitleScene(Scene):
    def setup(self):
        self.title_surface = asset_finder.load_img("title")

    @Scene.print_clockinfo
    def update(self, dt):
        self.screen.blit(self.title_surface, calc_center_pos(self.title_surface.get_size(), self.screen.get_size()))


def main():
    pygame.init()
    world = GameWorld()
    clock = pygame.time.Clock()
    screen_size = [640, 360]
    px_scale = 2
    display = pygame.display.set_mode(screen_size)
    screen = pygame.surface.Surface([size // px_scale for size in screen_size])
    scene_manager = SceneManager()
    scene_manager.add(TitleScene(screen), "title")
    running = True
    dt = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            scene_manager.handle_event(event)
        scene_manager.update(dt)
        pygame.transform.scale(screen, screen_size, display) # 3rd argument does display.blit()
        pygame.display.flip()
        dt = clock.tick(FPS)  # milliseconds
    pygame.quit()


if __name__ == "__main__":
    main()
