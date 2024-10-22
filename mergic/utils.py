from typing import Callable, Iterable
import functools
import time


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
