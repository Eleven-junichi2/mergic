# TODO: make tests
from collections import OrderedDict, deque
from dataclasses import dataclass
from pathlib import Path
import tomllib
import json
from typing import Iterable, Optional, Tuple
import os

import pygame
from pygame.event import Event
from pygame.math import Vector2

from mergic.components import (
    HasActions,
    HasCoordinate,
    HasSurface,
    HasVelocity,
)

from mergic import (
    ActionController,
    GameWorld,
    AssetFinder,
    GameMap,
    ImageAtlas,
    SceneManager,
    Scene,
    TextMenu,
)
from mergic.gui import (
    MenuUICursor,
    MenuUICursorStyle,
    MenuUIHighlightStyle,
    MenuUI,
    MenuUIPageIndicatorStyle,
    TextInputUI,
)
from mergic.utils import calc_center_pos
from mergic.entities import Player

# os.environ["SDL_IME_SHOW_UI"] = "1"
# os.environ["SDL_HINT_IME_SHOW_UI"] = "1"
os.environ["SDL_HINT_IME_SUPPORT_EXTENDED_TEXT"] = "1"

FPS = 60

ASSETS_DIR = Path(__file__).parent / "assets"

asset_finder = AssetFinder()
asset_finder.register("title", ASSETS_DIR / "imgs" / "title.png")
asset_finder.register("font", ASSETS_DIR / "fonts" / "k8x12L.ttf")
music_asset_names = asset_finder.register_all_in_dir(
    ASSETS_DIR / "sounds" / "musics", inclusive_exts=[".wav", ".ogg"]
)


@dataclass
class Config:  # unused
    music_volume: float
    sound_effect_volume: float


def load_config():
    with open(Path(__file__).parent / "config.toml", "r") as f:
        return tomllib.load(f)


def load_localized_texts(language_code="en"):
    with open(Path(__file__).parent / "i18n" / f"{language_code}.json", "r") as f:
        return json.load(f)


class SoundTestScene(Scene):
    def setup(self):
        self.font = asset_finder.load_font("font")
        self.font.size = 12
        self.font.fgcolor = pygame.color.Color(200, 200, 222)
        menu = TextMenu()
        menu.add_option(
            "Back to Title",
            key="back_to_title",
            callback=lambda: self.manager.change_scene("title", pygame.KEYDOWN),
        )
        for music_name in music_asset_names:
            menu.add_option(
                music_name, callback=self.manipulate_music_player, tag="music"
            )
        menucursor = MenuUICursor()
        menucursor.set_surface(
            self.font.render("♪", fgcolor=pygame.color.Color(255, 255, 255))[0]
        )
        self.menuui = MenuUI(
            menu,
            self.font,
            menucursor,
            highlight_style=MenuUIHighlightStyle(
                fgcolor=pygame.color.Color(255, 255, 255)
            ),
            max_display_options=6,
            page_indicator_style=MenuUIPageIndicatorStyle.ATTACH_BOTTOM,
        )
        self.menuui.focus()
        self.current_music: Optional[str] = None
        pygame.key.set_repeat(111, 111)

    def manipulate_music_player(self):
        current_selection = self.menuui.menu.current_selection()
        if current_selection[1]["tag"] == "music":
            if pygame.mixer_music.get_busy() and (
                self.current_music == current_selection[0]
            ):
                pygame.mixer_music.stop()
            else:
                pygame.mixer_music.load(asset_finder.filepath(current_selection[0]))
                pygame.mixer_music.play()
                self.current_music = current_selection[0]

    def cleanup(self):
        pygame.mixer_music.stop()
        pygame.mixer_music.unload()

    def handle_event(self, event: Event):
        self.menuui.handle_event(event)

    def update(self, dt):
        self.screen.blit(self.menuui.render(), (0, 0))


class TestMenuScene(Scene):
    def setup(self):
        self.font = asset_finder.load_font("font")
        self.font.size = 12
        self.font.fgcolor = pygame.color.Color(255, 255, 255)
        menu = TextMenu()
        menu.add_option("option1")
        menu.add_option("option2")
        menu.add_option("option3")
        menucursor = MenuUICursor()
        menucursor.set_surface(self.font.render("<>")[0])
        menucursor.set_render_position(MenuUICursorStyle.LEFT)
        self.menuui = MenuUI(menu, self.font, menucursor)
        self.menuui.focus()
        pygame.key.set_repeat(111, 111)

    def handle_event(self, event: Event):
        self.menuui.handle_event(event)

    def update(self, dt):
        self.screen.blit(self.menuui.render(), (0, 0))


class TitleScene(Scene):
    def setup(self):
        self.title_surface = asset_finder.load_img("title")
        self.title_pos = calc_center_pos(
            self.title_surface.get_size(), self.screen.get_size()
        )
        self.flag_gamescene = False
        self.font = asset_finder.load_font("font")
        self.font.size = 12
        self.font.fgcolor = pygame.color.Color(255, 255, 255)
        menu = TextMenu()
        menu.add_option(
            "Sound Test",
            callback=lambda: self.manager.change_scene(
                "sound_test", block_events_until_setup_finished=pygame.KEYDOWN
            ),
        )
        menu.add_option(
            "Battle Emulator",
            callback=lambda: self.manager.change_scene(
                "battle_emulation",
                block_events_until_setup_finished=(pygame.KEYDOWN, pygame.TEXTINPUT),
            ),
        )
        menu.add_option(
            "Exit", callback=lambda: pygame.event.post(pygame.event.Event(pygame.QUIT))
        )
        menucursor = MenuUICursor()
        menucursor.set_surface(self.font.render("<")[0])
        self.menuui = MenuUI(menu, self.font, menucursor)
        self.menuui.focus()
        pygame.key.set_repeat(111, 111)

    def handle_event(self, event: Event):
        self.menuui.handle_event(event)

    def update(self, dt):
        self.screen.fill((0, 0, 0))
        # self.screen.blit(
        #     self.title_surface,
        #     (self.title_pos[0], self.title_pos[1] // 2),
        # )
        self.screen.blit(self.menuui.render(), (0, self.title_pos[1] // 2 + 1))


class BattleEmulationScene(Scene):
    def setup(self):
        self.font = asset_finder.load_font("font")
        self.font.size = 12
        # self.font.fgcolor = pygame.color.Color(255, 255, 255)
        self.textinputui = TextInputUI(
            self.font, min_width_from_halfwidthchar_count=30, max_line_length=15
        )
        # self.textinputui.focus()
        self.menufont = asset_finder.load_font("font")
        self.menufont.size = 12
        self.menufont.fgcolor = pygame.color.Color(200, 200, 222)
        menu = TextMenu()
        menu.add_option(
            "テキスト入力をテスト", callback=lambda: (self.menuui.unfocus(),self.textinputui.focus())
        )
        menu.add_option(
            "足掻く",
        )
        menu.add_option("呪文")
        menu.add_option(
            "道具",
        )
        menu.add_option(
            "身を守る",
        )
        menu.add_option(
            "逃げる",
            callback=lambda: self.manager.change_scene("title", pygame.KEYDOWN),
        )
        self.menuui = MenuUI(
            menu,
            self.menufont,
            MenuUICursor(self.menufont.render("<")[0]),
            MenuUIHighlightStyle(fgcolor=pygame.color.Color(255, 255, 255)),
        )
        self.menuui.focus()
        pygame.key.set_repeat(156, 44)

    def handle_event(self, event: Event):
        self.textinputui.handle_event(event)
        self.menuui.handle_event(event)

    def update(self, dt):
        self.screen.fill((0, 0, 0))
        self.screen.blit(
            self.textinputui.render(),
            (0, 0),
        )
        self.screen.blit(
            self.menuui.render(),
            (0, 32),
        )


class GameScene(Scene):
    def setup(self):
        self.world = GameWorld()
        player_surf = pygame.Surface((16, 16))
        player_surf.fill(pygame.Color("red"))
        player = Player(
            pos=Vector2(0, 0),
            surface=player_surf,
            vel=Vector2(0, 0),
            actions=ActionController(),
        )
        player.actions.add_action("tile_movement_x", {})
        player.actions.add_action("tile_movement_y", {})
        self.world.add(player)

    def update(self, dt):
        self.screen.fill((0, 0, 0))
        scancode_map = pygame.key.get_pressed()
        for entity in self.world.entities_for_components(
            HasCoordinate, HasVelocity, HasSurface, HasActions
        ):
            if isinstance(entity, Player):
                vel_x = scancode_map[pygame.K_RIGHT] - scancode_map[pygame.K_LEFT]
                vel_y = scancode_map[pygame.K_DOWN] - scancode_map[pygame.K_UP]
                print("vx, vy", vel_x, vel_y)
                if vel_x != 0:
                    if not entity.actions.is_active("tile_movement_x"):
                        entity.actions.do("tile_movement_x")
                        entity.vel.x = vel_x
                else:
                    if not entity.actions.is_active("tile_movement_x"):
                        entity.vel.x = vel_x
                if entity.actions.is_active("tile_movement_x"):
                    entity.pos.x += 16 * entity.vel.x * dt / 1000
                    if round(entity.pos.x % 16) == 0:
                        entity.actions.cancel("tile_movement_x")

                if vel_y != 0:
                    if not entity.actions.is_active("tile_movement_y"):
                        entity.actions.do("tile_movement_y")
                        entity.vel.y = vel_y
                else:
                    if not entity.actions.is_active("tile_movement_y"):
                        entity.vel.y = vel_y
                if entity.actions.is_active("tile_movement_y"):
                    entity.pos.y += 16 * entity.vel.y * dt / 1000
                    if round(entity.pos.y % 16) == 0:
                        entity.actions.cancel("tile_movement_y")
            self.screen.blit(entity.surface, entity.pos)


def main():
    pygame.init()
    clock = pygame.time.Clock()
    screen_size = [640, 360]
    px_scale = 2
    display = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Wizahlen")
    screen = pygame.surface.Surface([size // px_scale for size in screen_size])
    scene_manager = SceneManager()
    scene_manager.add(TitleScene(screen), "title")
    scene_manager.add(SoundTestScene(screen), "sound_test")
    scene_manager.add(TestMenuScene(screen), "test_menu")
    scene_manager.add(GameScene(screen), "game")
    scene_manager.add(BattleEmulationScene(screen), "battle_emulation")
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
