# TODO: make tests
from pathlib import Path
import tomllib
import json

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


class TitleScene(Scene):
    def setup(self):
        self.title_surface = asset_finder.load_img("title")

    def update(self, dt):
        self.screen.blit(self.title_surface)
        print("title scene, dt: ", dt)


def main():
    pygame.init()
    # tileset = ImageAtlas(
    #     asset_finder.load_img("grass"),
    #     {"water": ((0, 0), (16, 16)), "grass": ((16, 0), (16, 16))},
    # )
    # tiletype_to_surface = {"grass": tileset.crop("grass"), "water": tileset.crop("water")}

    world = GameWorld()

    clock = pygame.time.Clock()
    display = pygame.display.set_mode((640, 360))
    scene_manager = SceneManager()
    scene_manager.add(Scene(display), "title")
    running = True
    dt = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            scene_manager.handle_event(event)
        scene_manager.update(dt)
        pygame.display.flip()
        dt = clock.tick(FPS)  # milliseconds
    pygame.quit()


if __name__ == "__main__":
    main()
