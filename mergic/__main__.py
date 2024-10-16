# TODO: make tests
from collections import OrderedDict, deque
from pathlib import Path
import tomllib
import json
from typing import Iterable, Tuple

import pygame
from pygame.event import Event
from pygame.math import Vector2

from mergic.components import (
    Actions,
    Coordinate,
    PygameSurface,
    TileCoordinate,
    TileVelocity,
    Velocity,
)

from mergic import (
    ActionController,
    GameWorld,
    AssetFinder,
    GameMap,
    ImageAtlas,
    MenuCursor,
    MenuCursorRenderPosition,
    MenuUI,
    SceneManager,
    Scene,
    TextMenu,
)
from mergic.calculation_tools import calc_center_pos
from mergic.entities import Player


FPS = 60

ASSETS_DIR = Path(__file__).parent / "assets"

asset_finder = AssetFinder()
asset_finder.register("title", ASSETS_DIR / "imgs" / "title.png")
asset_finder.register("font", ASSETS_DIR / "fonts" / "k8x12L.ttf")
music_asset_names = asset_finder.register_all_in_dir(
    ASSETS_DIR / "sounds" / "musics", inclusive_exts=[".wav", ".ogg"]
)
print(asset_finder.dict.keys())


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
        self.font.fgcolor = pygame.color.Color(255, 255, 255)
        menu = TextMenu()
        self.music_library: dict[str, pygame.mixer.Sound] = {}
        for name in music_asset_names:
            self.music_library[name] = asset_finder.load_sound(name)
        for music_name in self.music_library.keys():
            menu.add_option(music_name, callback=self.play_music)
        menucursor = MenuCursor()
        menucursor.set_surface(self.font.render("♪")[0])
        self.menuui = MenuUI(menu, self.font, menucursor)
        pygame.key.set_repeat(111, 111)
        pygame.event.set_allowed(pygame.KEYDOWN)

    def play_music(self):
        music_selection = self.menuui.menu.current_selection()[0]
        for name in self.music_library.keys():
            if name != music_selection:
                self.music_library[name].stop()
        self.music_library[music_selection].play()

    def handle_event(self, event: Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menuui.menu.selector_up()
            if event.key == pygame.K_DOWN:
                self.menuui.menu.selector_down()
            if event.key == pygame.K_SPACE:
                self.menuui.menu.execute_current_selection()

    def update(self, dt):
        print("hoo")
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
        menucursor = MenuCursor()
        menucursor.set_surface(self.font.render("<>")[0])
        menucursor.set_render_position(MenuCursorRenderPosition.LEFT)
        self.menuui = MenuUI(menu, self.font, menucursor)
        pygame.key.set_repeat(111, 111)
    
    def handle_event(self, event: Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menuui.menu.selector_up()
            if event.key == pygame.K_DOWN:
                self.menuui.menu.selector_down()

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
        menu.add_option("Sound Test", callback=lambda: self.change_scene("sound_test"))
        menu.add_option("Exit", callback=lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)))
        menucursor = MenuCursor()
        menucursor.set_surface(self.font.render("<")[0])
        self.menuui = MenuUI(menu, self.font, menucursor)
        pygame.key.set_repeat(111, 111)

    def handle_event(self, event: Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menuui.menu.selector_up()
            if event.key == pygame.K_DOWN:
                self.menuui.menu.selector_down()
            if event.key == pygame.K_SPACE:
                pygame.event.set_blocked(pygame.KEYDOWN)
                self.menuui.menu.execute_current_selection()

    def update(self, dt):
        self.screen.blit(
            self.title_surface,
            (self.title_pos[0], self.title_pos[1] // 2),
        )
        self.screen.blit(self.menuui.render(), (0, self.title_pos[1] // 2 + 1))


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
            Coordinate, Velocity, PygameSurface, Actions
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
    screen = pygame.surface.Surface([size // px_scale for size in screen_size])
    scene_manager = SceneManager()
    scene_manager.add(TitleScene(screen), "title")
    scene_manager.add(SoundTestScene(screen), "sound_test")
    scene_manager.add(TestMenuScene(screen), "test_menu")
    scene_manager.add(GameScene(screen), "game")
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
