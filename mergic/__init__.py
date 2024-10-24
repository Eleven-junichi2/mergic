from collections import OrderedDict, deque
from pathlib import Path
from typing import (
    Any,
    Callable,
    Generator,
    Iterable,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
)
from dataclasses import dataclass
import os

import pygame
import pygame.freetype

from mergic.gamemap import TileMap


class ECS:
    def __init__(self):
        self.entities: dict[type, list[object]] = {}
        self.dead_entity_buffer: list[object] = []

    def add(self, entity: object):
        self.entities.setdefault(entity.__class__, [])
        self.entities[entity.__class__].append(entity)

    def delete_now(self, entity):
        self.entities[entity.__class__].remove(entity)

    def reserve_to_delete(self, entity):
        if entity not in self.dead_entity_buffer:
            self.dead_entity_buffer.append(entity)

    def do_reserved_deletions(self):
        for entity in self.dead_entity_buffer:
            self.delete_now(entity)
        self.dead_entity_buffer.clear()

    def entities_for_type[T](self, entity_type: Type[T]) -> Generator[T, Any, None]:
        yield from self.entities[entity_type]

    def entities_for_components[T](
        self, *component_types: type[T]
    ) -> Generator[T, Any, None]:
        """TODO: fix this to be more efficient\n
        If you want to use a union type alias for `component_types`,
        you can do it with typing.get_args function converts the type alias to the tuple of types.
        """
        entities = deque()
        for entity_type in self.entities.keys():
            if set(component_types).issubset(entity_type.__mro__):
                entities.extend(self.entities_for_type(entity_type))
        yield from entities


class ActionController:
    def __init__(self):
        self.actions: dict[
            str, dict[str, bool | Any]
        ] = {}  # example: { "action_key": {"active": False, "property": {}}}

    def add_action(self, action: str, property: dict):
        self.actions.setdefault(action, {"active": False, "property": property})

    def mutable_property(self, action: str):
        return self.actions[action]["property"]

    def do(self, action: str):
        if self.actions.get(action, False):
            self.actions[action]["active"] = True
        else:
            raise ValueError(f"Action '{action}' is not registered")

    def cancel(self, action: str):
        if self.actions.get(action, False):
            self.actions[action]["active"] = False
        else:
            raise ValueError(f"Action '{action}' is not registered")

    def is_active(self, action: str) -> bool:
        return self.actions[action]["active"]


class GameWorld(ECS):
    def __init__(self):
        super().__init__()
        self.maps: dict[str, TileMap] = {}

    def map_for_name(self, map_name) -> TileMap:
        return self.maps.get(map_name)

    def set_map(self, map_name, tilemap: TileMap):
        self.maps[map_name] = tilemap


@dataclass
class Scene:
    screen: pygame.surface.Surface
    manager: Optional["SceneManager"] = None

    @staticmethod
    def print_clockinfo(fn: Callable, measurement_times=3):
        fps_history = deque()

        def wrapper(self, dt):
            fps_history.append(1 / (dt / 1000) if dt != 0 else 0)
            fn(self, dt)
            print(
                f"delta time: {dt}, FPS(Average over {measurement_times} measurements): {sum(fps_history) / len(fps_history)}"
            )
            if len(fps_history) > measurement_times:
                fps_history.popleft()

        return wrapper

    def setup(self):
        pass

    def cleanup(self):
        pass

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, dt):
        pass

    def change_scene(self, next_scene_name: str):
        self.manager.change_scene(next_scene_name)


class SceneManager:
    def __init__(self):
        self.current_scene: Optional[str] = None
        self.scenes: dict[str, Scene] = {}

    def add(self, scene: Scene, scene_name=str):
        flag_to_setup = True if len(self.scenes) == 0 else False
        scene.manager = self
        self.scenes[scene_name] = scene
        if flag_to_setup:
            self.current_scene = scene_name
            self.scenes[self.current_scene].setup()

    def change_scene(
        self,
        next_scene_name: str,
        block_events_until_setup_finished: Optional[Sequence[pygame.event.EventType]],
    ):
        if block_events_until_setup_finished:
            pygame.event.set_blocked(block_events_until_setup_finished)
        self.scenes[self.current_scene].cleanup()
        self.current_scene = next_scene_name
        self.scenes[self.current_scene].setup()
        if block_events_until_setup_finished:
            pygame.event.set_allowed(block_events_until_setup_finished)

    def handle_event(self, event: pygame.event.Event):
        self.scenes[self.current_scene].handle_event(event)

    def update(self, dt):
        self.scenes[self.current_scene].update(dt)


class TextMenu:
    def __init__(self):
        self.options: OrderedDict[str, Callable | str] = OrderedDict()
        self.__longest_text_length: int = 0
        self.__selector: int = 0

    @property
    def longest_text_length(self) -> int:
        return self.__longest_text_length

    @property
    def selector(self) -> int:
        return self.__selector

    @selector.setter
    def selector(self, value: int):
        self.__selector = value

    def selector_up(self):
        self.selector = (self.selector - 1) % len(
            self.options
        )  # selector番号がoption数と一致すると余りなし=0となるので選択をループできる

    def selector_down(self):
        self.selector = (self.selector + 1) % len(self.options)

    def selector_point_at(self, index: int):
        if index < 0 or len(self.options) < index:
            raise IndexError(f"Invalid index(max={len(self.options)})")
        self.selector = index

    def add_option(
        self,
        text: str,
        key: Optional[str] = None,
        callback: Optional[Callable] = None,
        tag: Optional[str] = None,
    ):
        text_length = len(text)
        self.__longest_text_length = (
            text_length
            if text_length > self.longest_text_length
            else self.longest_text_length
        )
        if key is None:
            key = text
        self.options[key] = {"text": text, "callback": callback, "tag": tag}

    def current_selection(self):
        return list(self.options.items())[self.selector]

    def execute_current_selection(self):
        if callback := self.current_selection()[1]["callback"]:
            return callback()
