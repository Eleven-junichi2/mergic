from dataclasses import dataclass, field
from typing import Callable, Iterable
import functools
import json
import os
import time

import pygame
import pygame.freetype


@dataclass(init=False)
class PromptResult[T]:
    """This class represents the result of a User Selection.
    The reason for wrapping the result in this class is to
    prevent values such as 0 and "" from being considered False."""

    value: T = field(init=False)
    _is_ok: bool = field(init=False)

    @classmethod
    def Ok(cls, value: T):
        wrapper = PromptResult[T]()
        wrapper.value = value
        wrapper._is_ok = True
        return wrapper

    @classmethod
    def Cancel(cls):
        wrapper = PromptResult[T]()
        wrapper._is_ok = False
        return wrapper

    def __bool__(self):
        return self._is_ok

    def unwrap(self) -> T:
        return self.value


def calc_center_pos(
    target_size: Iterable[int], canvas_size: Iterable[int]
) -> list[int, int]:
    """Calculate position of `target` to center it on the `canvas`"""
    return [csize // 2 - tsize // 2 for tsize, csize in zip(target_size, canvas_size)]


def measure_time_performance(func: Callable):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter_ns()
        print(f"run Func {func.__name__}")
        result = func(*args, **kwargs)
        end_time = time.perf_counter_ns()
        time.perf_counter()
        print(
            f"Func {func.__name__} took {(end_time - start_time)/(10**9):.9f} seconds, result={result}"
        )
        return result

    return wrapper


def load_json(filepath: str | os.PathLike):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_img(filepath: str | os.PathLike) -> pygame.Surface:
    return pygame.image.load(filepath)


def load_sound(filepath: str | os.PathLike) -> pygame.mixer.Sound:
    return pygame.mixer.Sound(filepath)


def load_font(filepath: str | os.PathLike) -> pygame.freetype.Font:
    return pygame.freetype.Font(filepath)
