from collections import UserDict
from dataclasses import dataclass, field
import os
from typing import Iterable

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

    def import_tiletype_map(self, mapdict: StrAsCoordMapDict | dict):
        self.tiletype_map = StrAsCoordMapDict(mapdict)


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
