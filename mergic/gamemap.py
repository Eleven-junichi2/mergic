from collections import UserDict
from dataclasses import dataclass, field
import os
from typing import Iterable, Optional

import pygame

from mergic.asset import AssetFinder, ImageAtlas
from mergic.utils import load_json


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
            key = ",".join([str(p) for p in key])
        return super().__setitem__(key, item)

    def coords_for_cells(self):
        yield from [
            [int(_) for _ in coordinate_str.split(",")]
            for coordinate_str in self.keys()
        ]


@dataclass
class TileMap:
    # TODO: rewrite test
    width: Optional[int] = None
    height: Optional[int] = None
    signed: bool = False
    trait_layers: dict[str, StrAsCoordMapDict] = field(default_factory=dict)
    terrain_layers: dict[str, StrAsCoordMapDict] = field(default_factory=dict)

    def paint_terrain(self, layer_id: str, x: int, y: int, brush):
        self._raise_if_invalid_coordinate(x, y)
        self.terrain_layers.setdefault(layer_id, StrAsCoordMapDict())
        self.terrain_layers[layer_id][f"{x},{y}"] = brush

    def paint_trait(self, layer_id: str, x: int, y: int, brush):
        self._raise_if_invalid_coordinate(x, y)
        self.trait_layers.setdefault(layer_id, StrAsCoordMapDict())
        self.trait_layers[layer_id][f"{x},{y}"] = brush

    def erase_terrain(self, layer_id: str, x: int, y: int):
        self._raise_if_invalid_coordinate(x, y)
        del self.terrain_layers[layer_id][f"{x},{y}"]

    def erase_trait(self, layer_id: str, x: int, y: int):
        self._raise_if_invalid_coordinate(x, y)
        del self.trait_layers[layer_id][f"{x},{y}"]

    def _is_coordinate_in_map(self, x: int, y: int):
        return (
            0 <= x < self.width and 0 <= y < self.height
            if self.signed
            else -self.width < x < self.width and -self.height < y < self.height
        )

    def _raise_if_invalid_coordinate(self, x: int, y: int):
        if not self._is_coordinate_in_map(x, y):
            raise ValueError(f"Invalid coordinate (out of range): x={x}, y={y}")

    def add_terrain_layer(self, layer_id: str):
        self.terrain_layers[layer_id] = StrAsCoordMapDict()

    def add_trait_layer(self, layer_id: str):
        self.trait_layers[layer_id] = StrAsCoordMapDict()

    def import_terrain_map(self, layer_id: str, mapdata: StrAsCoordMapDict):
        self.terrain_layers[layer_id] = mapdata

    def delete_terrain_layer(self, layer_id: str):
        del self.terrain_layers[layer_id]

    def import_trait_map(self, layer_id, mapdata: StrAsCoordMapDict | dict):
        self.trait_layers[layer_id] = StrAsCoordMapDict(mapdata)

    def delete_trait_layer(self, layer_id: str):
        del self.trait_layers[layer_id]


def register_imgs_and_existing_regions_files_in_dirs(
    img_dirpaths: Iterable[str | os.PathLike],
    asset_finder: AssetFinder,
    img_category_name: str = "img",
    atlas_regions_category_name: str = "atlas_regions",
):
    """
    指定されたディレクトリの画像を、`img_category_name`で指定されたカテゴリでAssetFinderに登録します。
    また、画像と同名のjsonファイルがあれば画像アトラスの領域指定を定義したものとして、
    `atlas_regions_category_name`で指定されたカテゴリ名でAssetFinderに登録します。
    返り値はそれぞれのアセット登録名のリスト2つです。
    """
    for tile_img_dirpath in img_dirpaths:
        img_asset_names = asset_finder.register_all_in_dir(
            img_category_name, tile_img_dirpath, inclusive_exts=(".png",)
        )
        atlas_regions_asset_names = asset_finder.register_all_in_dir(
            atlas_regions_category_name, tile_img_dirpath, inclusive_exts=(".json",)
        )
    return img_asset_names, atlas_regions_asset_names


def build_tileid_to_surf_from_img_dirs(
    asset_finder: AssetFinder,
    tile_img_assets_as_tileids: Iterable[str],
    img_category_name: str = "img",
    atlas_regions_category_name: str = "atlas_regions",
):
    tileid_to_surf = {}
    for img_asset_name in tile_img_assets_as_tileids:
        if img_asset_name in asset_finder.dict[atlas_regions_category_name].keys():
            atlas = ImageAtlas(
                asset_finder.load(img_asset_name, img_category_name, pygame.image.load),
                asset_finder.load(
                    img_asset_name, atlas_regions_category_name, load_json
                ),
                atlas_name=img_asset_name,
            )
            tileid_to_surf.update(atlas.name_to_surf_dict())
        else:
            tileid_to_surf[img_asset_name] = asset_finder.load_img(img_asset_name)
    return tileid_to_surf
