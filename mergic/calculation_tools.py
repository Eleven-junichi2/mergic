from typing import Iterable


def calc_center_pos(
    target_size: Iterable[int], canvas_size: Iterable[int]
) -> list[int, int]:
    """Calculate position of `target` to center it on the `canvas`"""
    return [csize // 2 - tsize // 2 for tsize, csize in zip(target_size, canvas_size)]
