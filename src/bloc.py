from __future__ import annotations
from typing import TYPE_CHECKING, Iterator, Optional

from pygame import Surface
import pygame

from .sprites import Sprite, get_image

if TYPE_CHECKING:
    from .map import Map

# Protocol :
# initialisation du bloc avec ses coordonnées, son parent et optionnelement ses données

BLOC_NAMES = [
    "grass",
    "sea",
    "path",
    "moulin",
    "gravel_path",
    "river",
    "muraille",
    "border",
    "bridge",
    "stone_bridge",
    "entrance",
    "lake"
]

class Tile:
    x: int
    y: int
    layers: Layers
    render: Optional[Surface]
    map: Map
    
    def __init__(
        self, x: int,
        y: int,
        parent: Map,
        data: Optional[int] = None,
        layers: Optional[Layers] = None
    ) -> None:
        self.x, self.y = x, y
        self.data = data
        self.map = parent
        self.id = None
        if layers is not None:
            self.layers = layers
            self.layers.tile = self
        else:
            self.layers = Layers(self)
        self.render_ = None

    def render(self, surface: Surface):
        if self.render_ is None:
            self.render_ = self.layers.render()
        x_destination = (self.x - self.map.camera_x) * 32 + surface.get_width()//2 - 16
        y_destination = (self.y - self.map.camera_y) * 32 + surface.get_height()//2 - 16
        surface.blit(
            self.render_,
            (x_destination, y_destination)
        )

    @property
    def hitbox(self) -> bool:
        return False

class LayerIndex:
    marker=-4
    wall=-3
    path=-2
    river=-1
    background=0
    content=1

"""
layers :
  0 background: la tuile de fond (peut être différente de celle par défaut du monde)
  -1 river: bool si une rivière doit être affichée à cet emplacement ou non
  -2 path: int le chemin qui doit être affiché sur la tuile (None=pas de chemin, 0=chemin marron, 1=chemin gris)
  -3 wall: int le mur qui doit être affiché sur la tuile (None pas de mur, 0=mur normal)
  2..+oo couches: List[?] les couches en dessous du contenu
  1 content: ? le contenu de la tuile (par ex un moulin, un lac...)
  -4 marker: ? si un joueur a posé un marqueur sur l'emplacement
"""

class Layers:
    tile: Tile
    
    def __init__(self, tile: Tile):
        self.tile = tile
        self._background = None
        self.muraille = Muraille(self.tile)
    
    def render(self) -> Surface:
        surface = Surface((32, 32), pygame.SRCALPHA)
        for layer in self:
            surface.blit(layer.render(), (0, 0))
        return surface

    def __iter__(self) -> Iterator[Bloc]:
        for layer in [
            self.background,
            self.muraille,
        ]:
            if layer is not None:
                yield layer

    @property
    def background(self) -> Optional[Bloc]:
        if self._background is not None:
            return self._background
        elif self.tile.map is not None:
            bloc = Bloc(self.tile)
            bloc.id = self.tile.map.background
            self._background = bloc
            return self.background
        else:
            return None
    
    @background.setter
    def background(self, bloc: Optional[Bloc]) -> None:
        self._background = bloc

class Bloc:
    sprite: Sprite
    
    def __init__(self, tile: Tile, data: int = 0) -> None:
        self.tile = tile
        self.data = data
        self.sprite = None
    
    def render(self) -> Surface:
        if self.sprite is None:
            self.sprite = get_image(BLOC_NAMES[self.id])
        animation_state = self.tile.map.animation_state if self.tile.map is not None else 0
        surface = self.sprite.image(self.data, animation_state, self.tile.x, self.tile.y)
        return surface

    def update(self) -> None:
        pass

class ConnectedBloc(Bloc):
    north: int
    south: int
    east: int
    west: int
    
    def update(self):
        self.north = self.tile.map[self.tile.x, self.tile.y-1].type == self.id
        self.south = self.tile.map[self.tile.x, self.tile.y+1].type == self.id
        self.east = self.tile.map[self.tile.x+1, self.tile.y].type == self.id
        self.west = self.tile.map[self.tile.x-1, self.tile.y].type == self.id
    
    @property
    def data(self) -> int:
        return self.north*(2**0) + self.south*(2**1) + self.west*(2**2) + self.east*(2**3)
    
    @data.setter
    def data(self, data: int) -> None:
        self.east = bool(data//(2**3))
        data = data % (2**3)
        self.west = bool(data//(2**2))
        data = data % (2**2)
        self.south = bool(data//(2**1))
        data = data % (2**1)
        self.north = bool(data//(2**0))

class Grass(Bloc):
    id=0

class Muraille(ConnectedBloc):
    id=6