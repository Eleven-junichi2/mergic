import pygame

from mergic import SceneManager, Scene
from mergic.mainloop_template import basic_mainloop


class HelloWorldScene(Scene):
    def handle_event(self, event: pygame.event.Event):
        print(event)

    def update(self, dt):
        print(dt)
        self.screen.fill((78, 222, 111))


if __name__ == "__main__":
    basic_mainloop(scenes={"hello_world": HelloWorldScene()})
