from pathlib import Path

import pygame
import pygame.freetype

from mergic import Scene
from mergic.utils import load_font
from mergic.asset import AssetFinder
from mergic.ui import MenuUI, MenuUIHighlightStyle, TextMenu
from mergic.mainloop_template import basic_mainloop

ASSETS_DIR = Path(__file__).parent / "assets"

asset_finder = AssetFinder()
asset_finder.register("retro", ASSETS_DIR / "fonts" / "k8x12L.ttf", category="font")


class UIScene(Scene):
    def setup(self):
        pygame.key.set_repeat(111, 111)
        font = asset_finder.load("retro", "font", load_font)
        font.size = 12
        font.fgcolor = pygame.color.Color(200, 200, 222)
        self.menu_ui = MenuUI(
            TextMenu(), font, highlight_style=MenuUIHighlightStyle(fgcolor=pygame.color.Color(255, 255, 255)), pos=(20, 20)
        )
        self.menu_ui.menu.add_option("Option A", "option_a")
        self.menu_ui.menu.add_option("Option B", "option_b")
        self.menu_ui.menu.add_option("Option C", "option_c")
        self.menu_ui.focus()

    def handle_event(self, event: pygame.event.Event):
        self.menu_ui.handle_event(event)

    def update(self, dt):
        self.screen.blit(self.menu_ui.render(), self.menu_ui.pos)


if __name__ == "__main__":
    basic_mainloop(scenes={"gui": UIScene()}, px_scale=2)
