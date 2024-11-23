import pygame

from mergic import Scene
from mergic.ui import MenuUI
from mergic.mainloop_template import basic_mainloop


class UIScene(Scene):
    def setup(self):
        self.menu_ui = MenuUI()

    def handle_event(self, event: pygame.event.Event):
        print(event)

    def update(self, dt):
        pass


if __name__ == "__main__":
    basic_mainloop(scenes={"gui": UIScene()})
