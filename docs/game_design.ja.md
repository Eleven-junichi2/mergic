# 仕様

## 概要

俯瞰視点の2D RPG。
魔法または技の連続発動による合成で異なる効果を楽しめる、
また、魔法の効果は入力した数値の性質によって変化する。

## グラフィック

16 x 16 のタイルマップ

## データ構造

tiletype_to_surf タイルの種類に対するpygame.Surfaceの辞書。str: pygame.Surface
assetname_to_filepath ファイルパスに対するエイリアス名辞書。 AssetFinderがこの役目を担う

## Integral Spell
