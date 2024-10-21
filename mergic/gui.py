from enum import Enum, auto
import os
from typing import (
    Optional,
)
from dataclasses import dataclass

import pygame
import pygame.freetype

from mergic import TextMenu


@dataclass
class MenuUIHighlightStyle:
    fgcolor: Optional[pygame.color.Color] = None
    bgcolor: Optional[pygame.color.Color] = None
    lerping_fgcolor_amount: Optional[float] = None
    lerping_bgcolor_amount: Optional[float] = None


class MenuUICursorStyle(Enum):
    ATTACH_LEFT = auto()
    ATTACH_RIGHT = auto()


class MenuUICursor:
    def __init__(self, surface: Optional[pygame.surface.Surface] = None, render_position: MenuUICursorStyle = MenuUICursorStyle.ATTACH_RIGHT):
        self.surface = surface
        self.render_position = render_position

    def set_surface(self, surface: pygame.surface.Surface):
        self.surface = surface

    def set_render_position(self, position: MenuUICursorStyle):
        self.render_position = position


class MenuUIAction(Enum):
    SELECTOR_UP = auto()
    SELECTOR_DOWN = auto()
    EXECUTE = auto()


class MenuUIViewMode(Enum):
    PAGING = auto()
    SCROLL = auto()  # not implemented


class MenuUIPageIndicatorStyle(Enum):
    ATTACH_BOTTOM = auto()
    ATTACH_TOP = auto()


class MenuUI:
    def __init__(
        self,
        menu: TextMenu,
        font: pygame.freetype.Font,
        cursor: Optional[MenuUICursor] = None,
        highlight_style: Optional[MenuUIHighlightStyle] = None,
        max_display_options: Optional[int] = None,
        view_mode: Optional[MenuUIViewMode] = MenuUIViewMode.PAGING,
        page_indicator_style: Optional[MenuUIPageIndicatorStyle] = None,
    ):
        self.menu = menu
        self.font = font
        self.cursor = cursor
        self.highlight_style = highlight_style
        self.surface_cache: Optional[pygame.surface.Surface] = (
            None  # unused TODO: implement
        )
        self.control_map = {
            pygame.KEYDOWN: {
                pygame.K_UP: MenuUIAction.SELECTOR_UP,
                pygame.K_DOWN: MenuUIAction.SELECTOR_DOWN,
                pygame.K_SPACE: MenuUIAction.EXECUTE,
            },
            pygame.MOUSEBUTTONDOWN: {
                pygame.BUTTON_WHEELUP: MenuUIAction.SELECTOR_UP,
                pygame.BUTTON_WHEELDOWN: MenuUIAction.SELECTOR_DOWN,
            },
        }
        self.max_display_options = max_display_options
        self.view_mode = view_mode
        self.is_focused = False
        self.page_indicator_style = page_indicator_style

    def focus(self):
        self.is_focused = True

    def unfocus(self):
        self.is_focused = False

    def handle_event(self, event: pygame.event.Event):
        if not self.is_focused:
            return
        if event.type == pygame.KEYDOWN:
            action = self.control_map[event.type].get(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            action = self.control_map[event.type].get(event.button)
        else:
            action = None
        if action == MenuUIAction.SELECTOR_UP:
            self.menu.selector_up()
        elif action == MenuUIAction.SELECTOR_DOWN:
            self.menu.selector_down()
        elif action == MenuUIAction.EXECUTE:
            self.menu.execute_current_selection()

    def render(self) -> pygame.surface.Surface:
        cursor_space_attach_left = 0
        cursor_space_attach_right = 0
        page_indicator_space_attach_top = 0
        if self.cursor:
            if self.cursor.render_position == MenuUICursorStyle.ATTACH_LEFT:
                cursor_space_attach_left = self.cursor.surface.get_width()
            if self.cursor.render_position == MenuUICursorStyle.ATTACH_RIGHT:
                cursor_space_attach_right = self.cursor.surface.get_width()
        if self.page_indicator_style == MenuUIPageIndicatorStyle.ATTACH_TOP:
            page_indicator_space_attach_top = self.font.size
        entire_surface = pygame.surface.Surface(
            (
                cursor_space_attach_left
                + self.font.size * self.menu.longest_text_length
                + cursor_space_attach_right,
                page_indicator_space_attach_top
                + self.font.size * len(self.menu.options),
            )
        )
        display_start = 0
        display_end = len(self.menu.options)
        if self.max_display_options:
            if self.view_mode == MenuUIViewMode.PAGING:
                display_start = self.max_display_options * (
                    self.menu.selector // self.max_display_options
                )
                display_end = self.max_display_options + display_start
            elif self.view_mode == MenuUIViewMode.SCROLL:
                raise NotImplementedError
        for i, option in enumerate(
            tuple(self.menu.options.values())[display_start:display_end]
        ):
            if i + display_start == self.menu.selector and self.highlight_style:
                fg = self.highlight_style.fgcolor
                if self.highlight_style.lerping_fgcolor_amount:
                    fg.lerp(
                        self.font.fgcolor, self.highlight_style.lerping_fgcolor_amount
                    )
                bg = self.highlight_style.bgcolor
                if self.highlight_style.lerping_bgcolor_amount:
                    bg.lerp(
                        self.font.bgcolor, self.highlight_style.lerping_bgcolor_amount
                    )
            else:
                fg = None
                bg = None
            text_surface, text_rect = self.font.render(
                option["text"], fgcolor=fg, bgcolor=bg
            )
            text_y = page_indicator_space_attach_top + i * text_rect.height
            if i + display_start == self.menu.selector and self.cursor:
                match self.cursor.render_position:
                    case MenuUICursorStyle.ATTACH_LEFT:
                        entire_surface.blit(self.cursor.surface, (0, text_y))
                    case MenuUICursorStyle.ATTACH_RIGHT:
                        entire_surface.blit(
                            self.cursor.surface, (text_rect.width, text_y)
                        )
            entire_surface.blit(
                text_surface,
                (cursor_space_attach_left, text_y),
            )
        if self.page_indicator_style:
            page_indicator_y = 0
            if self.page_indicator_style == MenuUIPageIndicatorStyle.ATTACH_BOTTOM:
                page_indicator_y = text_y + self.font.size
            entire_surface.blit(
                self.font.render(
                    f"Page:{self.menu.selector // self.max_display_options + 1}/{len(self.menu.options) // self.max_display_options + 1}",
                    fgcolor=self.font.fgcolor,
                    bgcolor=self.font.bgcolor,
                )[0],
                (0, page_indicator_y),
            )
        return entire_surface

    def update(self, dt):
        raise NotImplementedError


class SDL_IME_SHOW_UI_isInactiveError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TextInputUI:
    def __init__(
        self,
        font: pygame.freetype.Font,
        default_text: str = "",
        min_width_from_halfwidthchar_count: Optional[int] = None,
        max_line_length: Optional[int] = None,
        max_line_count: int = 1,
        fixed_width: Optional[int] = None,
        fixed_height: Optional[int] = None,
        bgcolor: Optional[pygame.color.Color] = None,
        bgcolor_on_focus: Optional[pygame.color.Color] = None,
    ):
        self.font = font
        self.text = default_text
        self.max_line_count = max_line_count
        self.min_width_from_halfwidthchar_count = min_width_from_halfwidthchar_count
        self.max_line_length = max_line_length
        self.fixed_width = fixed_width
        self.fixed_height = fixed_height
        self.bgcolor: pygame.color.Color = bgcolor if bgcolor else pygame.color.Color(222, 222, 222)
        self.bgcolor_on_focus: pygame.color.Color = bgcolor_on_focus if bgcolor_on_focus else pygame.color.Color(255, 255, 255)
        self.is_focused = False
        self.editing_text = ""

    def focus(self):
        pygame.key.start_text_input()
        self.is_focused = True

    def display_IME_candidate_list(self, where_to_render: Optional[pygame.rect.Rect]):
        if os.environ.get("SDL_IME_SHOW_UI", "0") == "0":
            raise SDL_IME_SHOW_UI_isInactiveError(
                "Enviroment variable 'SDL_IME_SHOW_UI' must be \"1\" to display IME candidate list. Please set it before Pygame initialization."
            )
        pygame.key.set_text_input_rect(where_to_render)

    def unfocus(self):
        pygame.key.stop_text_input()
        self.is_focused = False

    def render(self) -> pygame.surface.Surface:
        bgcolor = self.bgcolor_on_focus if self.is_focused else self.bgcolor
        lines = []
        longest_line = ""
        for line in self.text.splitlines():
            lines.append(line)
            longest_line = line if len(line) > len(longest_line) else longest_line
        editing_text_display = (
            self.editing_text + "…"
            if len(self.editing_text.encode()) > 29
            else self.editing_text
        )
        editing_text_surface, editing_text_rect = self.font.render(
            editing_text_display,
            fgcolor=bgcolor,
            bgcolor=pygame.color.Color(
                bgcolor.r ^ 255, bgcolor.g ^ 255, bgcolor.b ^ 255
            ),
        )
        longest_line_surface_width = self.font.get_rect(longest_line)[2]
        if longest_line_surface_width < editing_text_rect.width:
            longest_line_surface_width = editing_text_rect.width
        else:
            if self.min_width_from_halfwidthchar_count:
                min_width = self.font.get_rect(
                    " " * self.min_width_from_halfwidthchar_count
                )[2]
                if longest_line_surface_width < min_width:
                    longest_line_surface_width = min_width
        if self.fixed_width:
            longest_line_surface_width = self.fixed_width
        if self.fixed_height:
            height = self.fixed_height
        else:
            height = self.font.size * self.max_line_count
        entire_surface = pygame.surface.Surface((longest_line_surface_width, height))
        entire_surface.fill(bgcolor)
        for line_num, text in enumerate(lines):
            if line_num == self.max_line_count:
                break
            text_surface, text_rect = self.font.render(text)
            entire_surface.blit(
                text_surface,
                (0, line_num * text_rect[1]),
            )
        # pygame.draw.rect(entire_surface, bgcolor, (0, 0, *editing_text_rect.size))
        entire_surface.blit(editing_text_surface, (0, 0))
        self.surface_cache = entire_surface
        return entire_surface

    def handle_event(self, event: pygame.event.Event):
        if not self.is_focused:
            return
        if event.type == pygame.TEXTEDITING:
            self.editing_text = event.text
            print(
                f"editing_text='{self.editing_text}', TEXTEDITING: text={event.text} start={event.start} length={event.length}"
            )
        if event.type == pygame.TEXTINPUT:
            print(f"beforeedit: self.text='{self.text}' TEXTINPUT: text='{event.text}'")
            self.text += event.text
            if self.max_line_length:
                self.text = self.text[: self.max_line_length]
            # print(f"afteredit: self.text='{self.text}' TEXTINPUT: text='{event.text}'")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                # print(f"afteredit: self.text='{self.text}'")
