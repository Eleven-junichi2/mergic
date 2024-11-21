import pygame

from mergic import SceneManager, Scene


class HelloWorldScene(Scene):
    def handle_event(self, event: pygame.event.Event):
        print(event)

    def update(self, dt):
        print(dt)
        self.screen.fill((0, 255, 0))


def main():
    FPS = 60
    pygame.init()
    clock = pygame.time.Clock()
    screen_size = (640, 360)
    px_scale = 2
    display = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Hello world!")
    screen = pygame.surface.Surface([size // px_scale for size in screen_size])
    scene_manager = SceneManager()
    scene_manager.add(HelloWorldScene(screen), "hello_world")
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
