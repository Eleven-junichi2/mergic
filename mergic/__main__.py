# TODO: make tests
from pathlib import Path
import tomllib
import json

import pygame

from . import GameWorld, AssetFinder, GameMap, ImageAtlas


FPS = 60

ASSETS_DIR = Path(__file__).parent / "assets"


def load_config():
    with open(Path(__file__).parent / "config.toml", "r") as f:
        return tomllib.load(f)


def load_localized_texts(language_code="en"):
    with open(Path(__file__).parent / "i18n" / f"{language_code}.json", "r") as f:
        return json.load(f)


def main():
    pygame.init()

    asset_finder = AssetFinder()
    asset_finder.register("grass", ASSETS_DIR / "imgs" / "terrain" / "Grass.png")
    tileset = ImageAtlas(
        asset_finder.load_img("grass"),
        {"water": ((0, 0), (16, 16)), "grass": ((16, 0), (16, 16))},
    )
    tiletype_to_surface = {"grass": tileset.crop("grass"), "water": tileset.crop("water")}

    world = GameWorld()
    world.set_gamemap("departure", GameMap(16, 16))
    world.gamemap("departure").import_layer(
        "ground", {(0, 0): "grass", (4, 4): "water"}
    )

    clock = pygame.time.Clock()
    display = pygame.display.set_mode((640, 360))
    running = True
    dt = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        display.fill((0, 0, 0))
        for y in range(0, world.gamemap("departure").height):
            for x in range(0, world.gamemap("departure").width):
                display.blit(
                    tiletype_to_surface[
                        world.gamemap("departure").layer("ground").get((x, y), "water")
                    ],
                    (x * 16, y * 16),
                )
        pygame.display.flip()
        dt = clock.tick(FPS)  # milliseconds
        # print(dt)
    pygame.quit()


if __name__ == "__main__":
    main()
