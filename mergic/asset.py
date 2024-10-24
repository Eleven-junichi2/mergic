from collections import deque
import os
from pathlib import Path
from typing import Callable, Optional, Tuple
import pygame
import pygame.freetype


class AssetFinder:
    def __init__(self):
        self.dict: dict[str, dict[str, str | os.PathLike]] = {}

    def register(self, name: str, filepath: str | os.PathLike, category: str):
        if category not in self.dict:
            self.dict[category] = {}
        self.dict[category][name] = filepath

    def register_all_in_dir(
        self,
        category: str,
        dirpath: str | os.PathLike,
        naming_with_suffix: bool = False,
        inclusive_exts: Optional[Tuple[str]] = None,
        exclusive_exts: Optional[Tuple[str]] = None,
    ):
        registered_names = deque()
        for filepath in Path(dirpath).iterdir():
            if filepath.is_file():
                if inclusive_exts:
                    if filepath.suffix not in inclusive_exts:
                        continue
                if exclusive_exts:
                    if filepath.suffix in exclusive_exts:
                        continue
                if naming_with_suffix:
                    name = filepath.name
                else:
                    name = filepath.stem
                self.register(name, filepath, category)
                registered_names.append(name)
        return registered_names

    def load_img(self, name: str) -> pygame.Surface:
        return pygame.image.load(self.dict["img"][name])

    def load_sound(self, name: str) -> pygame.mixer.Sound:
        return pygame.mixer.Sound(str(self.dict["sound"][name]))

    def load_font(self, name: str) -> pygame.freetype.Font:
        return pygame.freetype.Font(str(self.dict["font"][name]))

    def load[T](
        self, name: str, category: str, loader: Callable[[str | os.PathLike], T]
    ) -> T:
        return loader(self.dict[category][name])

    def filepath(self, name: str, category: str) -> str | os.PathLike:
        return self.dict[category][name]


class ImageAtlas:
    def __init__(
        self,
        image: pygame.Surface,
        regions: dict[str, Tuple[Tuple[int, int], Tuple[int, int]]],
        atlas_name: Optional[str] = None,
    ):
        self.atlas_name = atlas_name
        self.image = image
        self.regions = regions

    def crop(self, region_name: str) -> pygame.Surface:
        if region_name not in self.regions:
            raise ValueError("Invalid region name")
        return self.image.subsurface(
            self.regions[region_name][0], self.regions[region_name][1]
        )

    def name_to_surf_dict(self, spliter_symbol: str = ":") -> dict[str, pygame.Surface]:
        """Create a dictionary with the structure 'region name: surface'.
        If `atlas_name` attribute is provided, the keys will be formatted as '{atlas_name}{spliter_symbol}{region_name}'.
        """
        if self.atlas_name:
            prefix = f"{self.atlas_name}{spliter_symbol}"
        else:
            prefix = ""
        return {
            f"{prefix}{atlas_name}": self.crop(atlas_name)
            for atlas_name in self.regions.keys()
        }


def atlas_filepaths_in_dir(
    dirpath: str | os.PathLike, regions_fileext=".json", atlas_fileext=".png"
):
    """return (regions filepath, image atlas filepath)"""
    dirpath = Path(dirpath)
    for filepath in dirpath.iterdir():
        if filepath.suffix == regions_fileext:
            if (
                atlas_filepath := (dirpath / f"{dirpath.stem}{atlas_fileext}")
            ).exists():
                yield (filepath, atlas_filepath)


def img_filepaths_without_atlas_in_dir(
    dirpath: str | os.PathLike, atlas_regions_fileext=".json", img_fileext=".png"
):
    dirpath = Path(dirpath)
    for filepath in dirpath.iterdir():
        if filepath.suffix == img_fileext:
            if not (dirpath / f"{dirpath.stem}{atlas_regions_fileext}").exists():
                yield filepath


def atlas_or_non_atlas_img_filepaths(
    dirpath: str | os.PathLike, atlas_regions_fileext=".json", img_fileext=".png"
):
    """
    return (regions filepath, image atlas filepath) if atlas\n
    return  (regions None, image atlas filepath) if not atlas
    """
    dirpath = Path(dirpath)
    for filepath in dirpath.iterdir():
        if filepath.suffix == img_fileext:
            if (
                regions_filepath := (dirpath / f"{dirpath.stem}{atlas_regions_fileext}")
            ).exists():
                yield (regions_filepath, filepath)
            else:
                yield (None, filepath)
