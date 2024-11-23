from typing import Optional
import pygame

from mergic import SceneManager, Scene


def basic_mainloop(scenes: dict[str, Scene], screen_size=(640, 360), px_scale=1, caption: Optional[str]=None, fps=60):
    pygame.init()
    clock = pygame.time.Clock()
    screen_size = (640, 360)
    display = pygame.display.set_mode(screen_size)
    if caption:
        pygame.display.set_caption(caption)
    screen = pygame.surface.Surface([size // px_scale for size in screen_size])
    scene_manager = SceneManager(scenes=scenes, screen=screen)
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
        dt = clock.tick(fps)  # milliseconds
    pygame.quit()
