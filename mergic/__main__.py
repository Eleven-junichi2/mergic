# TODO: make tests
from pathlib import Path

import pygame

from . import GameWorld, AssetFinder, GameMap
from .entities import Player

FPS = 60


def main():
    pygame.init()

    asset_finder = AssetFinder()

    world = GameWorld()
    world.set_gamemap("departure", GameMap(16, 16))
    world.maps["departure"].import_layer("ground", {(0, 0): 1, (4, 4): 1})
    for y in range(0, world.maps["departure"].height):
        for x in range(0, world.maps["departure"].width):
            print(world.maps["departure"].get_layer("ground").get((x, y), 0), end="")
        print()

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
        dt = clock.tick(FPS)  # milliseconds
        # print(dt)
    pygame.quit()


if __name__ == "__main__":
    main()
