# TODO: make tests
from pathlib import Path

import pygame

from . import GameWorld, AssetFinder
from .entities import Player

FPS = 60


def main():
    pygame.init()

    asset_finder = AssetFinder()

    player = Player(asset_finder.load_img("player"))

    world = GameWorld()
    world.add(player)

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
