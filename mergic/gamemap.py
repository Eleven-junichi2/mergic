from collections import UserDict
from dataclasses import dataclass, field
from typing import Any


class StrAsCoordMapDict[T](UserDict[str, T]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, key: str | tuple[int, ...]) -> T:
        if isinstance(key, tuple):
            key = ",".join([str(i) for i in key])
        item = super().__getitem__(key)
        return item
    
    def __setitem__(self, key: str | tuple[int, ...], item: T) -> None:
        if isinstance(key, tuple):
            key = ",".join([str(i) for i in key])
        return super().__setitem__(key, item)

    def coords_for_cells(self):
        yield from [
            [int(_) for _ in coordinate_str.split(",")]
            for coordinate_str in self.keys()
        ]


@dataclass
class TileMap:
    # TODO: rewrite test
    width: int
    height: int
    tiletype_map: StrAsCoordMapDict = field(default_factory=StrAsCoordMapDict)
    tileid_layers: dict[str, StrAsCoordMapDict] = field(
        default_factory=StrAsCoordMapDict
    )

    def paint_tileid(self, layer_id: str, x: int, y: int, brush):
        self._raise_if_invalid_coordinate(x, y)
        self.tileid_layers.setdefault(layer_id, StrAsCoordMapDict())
        self.tileid_layers[layer_id][f"{x},{y}"] = brush

    def paint_tiletype(self, x: int, y: int, brush):
        self._raise_if_invalid_coordinate(x, y)
        self.tileid_layers[f"{x},{y}"] = brush

    def erase_tileid(
        self,
        layer_id: str,
        x: int,
        y: int,
    ):
        self._raise_if_invalid_coordinate(x, y)
        del self.tileid_layers[layer_id][f"{x},{y}"]

    def _is_coordinate_in_map(self, x: int, y: int):
        return 0 <= x < self.width and 0 <= y < self.height

    def _raise_if_invalid_coordinate(self, x: int, y: int):
        if not self._is_coordinate_in_map(x, y):
            raise ValueError(f"Invalid coordinate (out of range): x={x}, y={y}")

    def import_layer(self, layer_id: str, mapdict: StrAsCoordMapDict):
        self.tileid_layers[layer_id] = mapdict

    def delete_layer(self, layer_id: str):
        del self.tileid_layers[layer_id]

    def import_tiletype_map(self, mapdict: StrAsCoordMapDict):
        self.tiletype_map = mapdict
