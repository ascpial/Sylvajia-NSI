from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING, Union

import json
from discordsdk.sdk import DiscordTimestamp

import pygame

from .maze_generator import Maze
from .discord import Discord
from .enums import Channels, World, WorldKey, WorldType
from .payloads import Payload
from .sprites import Sprite

if TYPE_CHECKING:
    from .game import Pygame

__all__ = [
    "types",
    "blocs_metadata",
    "get_type",
    "Tile",
    "Connected",
    "ElaborateConnected",
    "OneWayConnected",
    "Map"
]

types = [
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

with open("./data/blocs.json") as file:
    blocs_metadata: List[Dict[str, Any]] = json.load(file)

def get_type(type):
    if type in [2, 4, 5, 6]:
        cls = Connected
    elif type in [7]:
        cls = ElaborateConnected
    elif type in [8, 9, 10]:
        cls = OneWayConnected
    else:
        cls = Tile
    return cls

class Tile:
    """Classe représentant une tuile du jeu (un "bloc")"""
    x: int
    y: int
    type: int
    data: int
    background: Optional[Tile]

    # def __new__(cls: Tile, x: int, y: int, type: int, data: int, parent: Map, background: Tile = None) -> Union[Tile, Connected, ElaborateConnected]:
    #     if type in [2, 4, 5] and cls is not Connected:
    #         return Connected(x, y, type, data, parent, background)
    #     elif type in [7] and cls is not ElaborateConnected:
    #         return ElaborateConnected(x, y, type, data, parent, background)
    #     else:
    #         return super(Tile, cls).__new__(cls)

    def __init__(self, x: int, y: int, type: int, data: int, parent: Map, background: Optional[Tile] = None) -> None:
        """Initialise la tuile.
        Cette fonction prépare la classe pour lui permettre de fonctionner correctement
        
        Attributes
        ----------
        x: int
            La coordonnée `x` de la tuile
        y: int
            La coordonnée `y` de la tuile
        type: int
            Le type de tuile (la version du type lisible est trouvable dans la liste `types`)
        data: int
            Les données de la tuile.
            Typiquement, cette valeur indique si la tuile est connectée ou non.
        parent: Map
            Le parent de la tuile
            Cette valeur est utilisée afin de récupérer certaines informations comme par exemple lors de la mise à jour de la tuile
            (récupérer les tuiles voisines, etc...)
        background: Optional[Tile] = None
            Si la tuile a un fond, ce fond est alors spécifié ici.
        """
        self.x, self.y = x, y
        self.type = type
        self.hitbox = blocs_metadata[self.type].get('hitbox', False)
        self.data = data
        self.parent = parent
        self.background = background

    @property
    def sprite(self) -> Sprite:
        """Retourne le Sprite (la texture) correspondante à la tuile.
        
        Returns
        -------
        Sprite
            La texture de la tuile
        """
        return Sprite(types[self.type], self.data)
    
    def render(self, surface: pygame.Surface):
        """Traite le rendu de la tuile sur la surface données.
        La surface est un objet utilisé par pygame sur lequel on peut dessiner.
        
        Attributes
        ----------
        surface: pygame.Surface
            La surface sur laquelle afficher la tuile.
        """
        # on récupère les coordonnées de la tuile sur l'écran en fonction de la position de la caméra.
        x = (self.x - self.parent.camera_x) * 32 + surface.get_width()//2
        y = (self.y - self.parent.camera_y) * 32 + surface.get_height()//2

        sprite = self.sprite
        # on met la tuile au bon emplacement
        sprite.center_at(x, y)

        #on affiche le fond si besoin puis la tuile actuelle
        if self.background is not None:
            self.background.render(surface)
        sprite.blit(surface, self.parent.animation_state, self.x, self.y)
    
    def update(self, recursive: bool = True) -> None:
        """Met à jour les données de la tuile, implémenté par des sous-classes.
        Cette fonction peut être écrasée et ne fait rien par défaut.
        
        Attributes
        ----------
        recursive: bool = True
            Ne fait rien pour l'instant mais à terme permet de faire une mise à jour en cascade
        """
        pass

    def __repr__(self) -> str:
        """Retourne une chaîne de caractère représentant la tuile"""
        return f"<Tile Object type={self.type} x={self.x} y={self.y}>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Cette fonction retourne la tuile sous forme de dictionnaire.
        
        Returns
        -------
        Dict[str, Any]
            Le dictionnaire représentant la tuile
        """
        state = {
            "type": self.type,
            "x": self.x,
            "y": self.y,
            "data": self.data,
            "background": self.background.to_dict() if self.background is not None else None,
        }
        return state
    
    @classmethod
    def from_dict(cls, dict: Dict[str, Any], parent: Pygame) -> Tile:
        x, y = dict.get("x", 0), dict.get("y", 0)
        type = dict.get("type", 0)
        data = dict.get("data", 0)
        if "background" in dict and dict["background"] is not None:
            background = Tile.from_dict(dict["background"], parent)
        else:
            background = None
        class_type = get_type(type)
        return class_type(x, y, type, data, parent, background)


class Connected(Tile):
    """Représente une tuile utilisant de la connexion avec ses voisins"""
    top: bool = True
    bottom: bool = True
    right: bool = True
    left: bool = True

    def __init__(self, x: int, y: int, type: int, data: int, parent: Map, background: Optional[Tile] = None) -> None:
        """Initialise la tuile connectée avec un appel à Tile.__init__ et en initialisant les données des voisins
        Cette fonction prépare la classe pour lui permettre de fonctionner correctement
        Par rapport à la classe parente, cette classe regarde les tuiles voisines et change ses données en conséquence si
        besoin est de se connecter aux voisines (comme par exemple un chemin à un autre chemin ou à un pont...)
        
        Attributes
        ----------
        x: int
            La coordonnée `x` de la tuile
        y: int
            La coordonnée `y` de la tuile
        type: int
            Le type de tuile (la version du type lisible est trouvable dans la liste `types`)
        data: int
            Les données de la tuile.
            Typiquement, cette valeur indique si la tuile est connectée ou non.
        parent: Map
            Le parent de la tuile
            Cette valeur est utilisée afin de récupérer certaines informations comme par exemple lors de la mise à jour de la tuile
            (récupérer les tuiles voisines, etc...)
        background: Optional[Tile] = None
            Si la tuile a un fond, ce fond est alors spécifié ici.
        """
        super().__init__(x, y, type, data, parent, background)
        if self.type in [2, 4]:
            self.connected = [2, 4]
        elif type == 5:
            self.connected = [5, 8, 9]
        elif type == 6:
            self.connected = [6, 10]
        else:
            self.connected = []

    @property
    def data(self) -> int:
        """Retourne les données de la tuile en utilisant les variables de connexion local"""
        return self.top*(2**0) + self.bottom*(2**1) + self.left*(2**2) + self.right*(2**3)

    @data.setter
    def data(self, data: int) -> None:
        """Met à jour les données de la tuile en dépaquetant l'entier passé en paramètre"""
        self.right = bool(data//(2**3))
        data = data % (2**3)
        self.left = bool(data//(2**2))
        data = data % (2**2)
        self.bottom = bool(data//(2**1))
        data = data % (2**1)
        self.top = bool(data//(2**0))
    
    def update(self, recursive: bool = True) -> None:
        """Met à jour les données de la tuile en prenant en compte les connexions aux tuiles voisines
        
        Attributes
        ----------
        recursive: bool = True
            Ne fait rien pour l'instant mais à terme permet de faire une mise à jour en cascade
        """
        self.top = self.get_data(self.x, self.y-1)
        self.bottom = self.get_data(self.x, self.y+1)
        self.left = self.get_data(self.x-1, self.y)
        self.right = self.get_data(self.x+1, self.y)
        if sum([self.top, self.bottom, self.left, self.right]) == 1:
            # Si une seule des branches est liée, on active aussi celle en face pour faire une ligne dans la continuité
            reverse = {
                0: "bottom",
                1: "top",
                2: "right",
                3: "left"
            }
            setattr(self, reverse[[self.top, self.bottom, self.left, self.right].index(True)], True)
        elif sum([self.top, self.bottom, self.left, self.right]) == 0:
            self.data = 15
    
    def get_data(self, x: int, y: int) -> bool:
        """Retourne les données de connexion correspondant à la tuile aux coordonnées `x` et `y`"""
        return self.parent[x, y].type in self.connected

class ElaborateConnected(Tile):
    """Représente une tuile possédant une connexion élaborée, avec deux types de voisins : le bord et intérieur."""
    top: int = 1
    bottom: int = 1
    left: int = 1
    right: int = 1
    connected: List[int]
    inside: List[int]

    def __init__(self, x: int, y: int, type: int, data: int, parent: Map, background: Optional[Tile] = None) -> None:
        """Initialise la tuile connectée avec un appel à Tile.__init__ et en initialisant les données des voisins
        
        Attributes
        ----------
        x: int
            La coordonnée `x` de la tuile
        y: int
            La coordonnée `y` de la tuile
        type: int
            Le type de tuile (la version du type lisible est trouvable dans la liste `types`)
        data: int
            Les données de la tuile.
            Typiquement, cette valeur indique si la tuile est connectée ou non.
        parent: Map
            Le parent de la tuile
            Cette valeur est utilisée afin de récupérer certaines informations comme par exemple lors de la mise à jour de la tuile
            (récupérer les tuiles voisines, etc...)
        background: Optional[Tile] = None
            Si la tuile a un fond, ce fond est alors spécifié ici.
        """
        super().__init__(x, y, type, data, parent, background)
        if self.type == 7:
            self.connected = [7]
            self.inside = [0]
        else:
            self.connected = []
            self.inside = []
    
    @property
    def data(self) -> int:
        """Retourne les données de la tuile en utilisant les variables de connexion local"""
        data = self.top + self.bottom*(3**1) + self.left*(3**2) + self.right*(3**3)
        return data
    
    @data.setter
    def data(self, data: int) -> None:
        """Met à jour les données de la tuile en dépaquetant l'entier passé en paramètre"""
        self.right = data//(3**3)
        data = data % (3**3)
        self.left = data//(3**2)
        data = data % (3**2)
        self.bottom = data//(3**1)
        data = data % (3**1)
        self.top = data//(3**0)
    
    def update(self, recursive=True) -> None:
        """Met à jour les données de la tuile en prenant en compte les connexions aux tuiles voisines
        
        Attributes
        ----------
        recursive: bool = True
            Ne fait rien pour l'instant mais à terme permet de faire une mise à jour en cascade
        """
        self.top = self.get_value(self.x, self.y-1)
        self.bottom = self.get_value(self.x, self.y+1)
        self.left = self.get_value(self.x-1, self.y)
        self.right = self.get_value(self.x+1, self.y)
    
    def get_value(self, x: int, y: int) -> int:
        """Retourne les données de connexion correspondant à la tuile aux coordonnées `x` et `y`"""
        tile = self.parent[x, y]
        data = 1 if tile.type in self.connected else 2 if tile.type in self.inside else 0
        if data == 0 and tile.background is not None:
            data = 1 if tile.background.type in self.connected else 2 if tile.background.type in self.inside else 0
        return data

class OneWayConnected(Tile):
    """Représente une tuile utilisant de la connexion dans une direction avec ses voisins"""
    data: int = 0
    back_tile: Optional[Tile] = None
    linked_tile: Optional[Tile] = None

    def __init__(self, x: int, y: int, type: int, data: int, parent: Map, background: Optional[Tile] = None) -> None:
        """Initialise la tuile connectée avec un appel à Tile.__init__ et en initialisant les données des voisins
        
        Attributes
        ----------
        x: int
            La coordonnée `x` de la tuile
        y: int
            La coordonnée `y` de la tuile
        type: int
            Le type de tuile (la version du type lisible est trouvable dans la liste `types`)
        data: int
            Les données de la tuile.
            Typiquement, cette valeur indique si la tuile est connectée ou non.
        parent: Map
            Le parent de la tuile
            Cette valeur est utilisée afin de récupérer certaines informations comme par exemple lors de la mise à jour de la tuile
            (récupérer les tuiles voisines, etc...)
        background: Optional[Tile] = None
            Si la tuile a un fond, ce fond est alors spécifié ici.
        """
        super().__init__(x, y, type, data, parent, background)
        if self.type == 8:
            self.connected = 5
            self.linked = [2, 4]
        if self.type == 9:
            self.connected = 5
            self.linked = [2, 4]
        if self.type == 10:
            self.connected = 6
            self.linked = [2, 4, 5]
    
    def update(self, recursive: bool = True) -> None:
        """Met à jour les données de la tuile en prenant en compte les connexions aux tuiles voisines
        
        Attributes
        ----------
        recursive: bool = True
            Ne fait rien pour l'instant mais à terme permet de faire une mise à jour en cascade
        """
        self.data = self.get_data(self.x, self.y+1)
        self.back_tile = self.parent.get_tile(self.x, self.y, self.connected, 0)
        self.back_tile.update(recursive=False)
        if self.data:
            if self.parent[self.x-1, self.y].type in self.linked:
                type_linked = self.parent[self.x-1, self.y].type
            elif self.parent[self.x+1, self.y].type in self.linked:
                type_linked = self.parent[self.x+1, self.y].type
            else:
                type_linked = None
        else:
            if self.parent[self.x, self.y-1].type in self.linked:
                type_linked = self.parent[self.x, self.y-1].type
            elif self.parent[self.x, self.y+1].type in self.linked:
                type_linked = self.parent[self.x, self.y+1].type
            else:
                type_linked = None
        if type_linked is not None:
            self.linked_tile = self.parent.get_tile(self.x, self.y, type_linked)
            self.linked_tile.update()
    
    def get_data(self, x: int, y: int) -> bool:
        """Retourne les données de connexion correspondant à la tuile aux coordonnées `x` et `y`"""
        return self.parent[x, y].type == self.connected
    
    def render(self, surface: pygame.Surface):
        """Traite le rendu de la tuile sur la surface passé en paramètre
        La surface est un objet utilisé par pygame sur lequel on peut dessiner.
        
        Attributes
        ----------
        surface: pygame.Surface
            La surface sur laquelle afficher la tuile.
        """
        x = (self.x - self.parent.camera_x) * 32 + surface.get_width()//2
        y = (self.y - self.parent.camera_y) * 32 + surface.get_height()//2
        sprite = self.sprite
        sprite.center_at(x, y)
        if self.background is not None:
            self.background.render(surface)
        if self.linked_tile is not None:
            self.linked_tile.render(surface)
        if self.back_tile is not None:
            self.back_tile.render(surface)
        sprite.blit(surface, self.parent.animation_state, self.x, self.y)

class Map:
    """Classe contenant toutes les données des tuiles et permettant certaines actions sur le monde"""

    map: List[List[Tile]]
    background: int # type de la tuile de remplissage 
    parent: Pygame

    def __init__(self, parent: Pygame, width=30, height=30, generate_maze=True) -> None:
        """Initialise le monde (en version actuelle, une génération est effectuée)
        
        Attributes
        ----------
        parent: Any
        """
        self.parent = parent

        # self.map = [
        #     [
        #         TileTest(x, y, parent=self) for x in range(15)
        #     ] for y in range(15)
        # ]
        # self.spawn = [0, 0]
        # self.background = 1

        if generate_maze:
            self.background = 1

            self.MAZE_WIDTH = 30
            self.MAZE_HEIGHT = 30

            self.WIDTH = self.MAZE_WIDTH * 2 + 3
            self.HEIGHT = self.MAZE_HEIGHT * 2 + 3

            self.maze = Maze(self.MAZE_WIDTH, self.MAZE_HEIGHT)
            self.maze.generate()

            self.map = [
                [
                    self.get_tile(x, y, 0) for x in range(self.WIDTH)
                ] for y in range(self.HEIGHT)
            ]

            for y in range(self.HEIGHT):
                self[0, y]=self.get_tile(0, y, 7, 0, 1, 0)
                self[self.WIDTH-1, y]=self.get_tile(self.WIDTH-1, y, 7, 0, 1, 0)
            for x in range(self.WIDTH):
                self[x, 0]=self.get_tile(x, 0, 7, 0, 1, 0)
                self[x, self.HEIGHT-1]=self.get_tile(x, self.HEIGHT-1, 7, 0, 1, 0)
            
            for y in range(1, self.HEIGHT, 2):
                for x in range(1, self.WIDTH, 2):
                    self[x, y] = self.get_tile(x, y, 6, 0, 0)
                
            for row in self.maze.cells:
                for cell in row:
                    x, y = cell.x*2+2, cell.y*2+2
                    if cell.O:
                        self[x-1, y] = self.get_tile(x-1, y, 6, 0, 0)
                    if cell.E:
                        self[x+1, y] = self.get_tile(x+1, y, 6, 0, 0)
                    if cell.N:
                        self[x, y-1] = self.get_tile(x, y-1, 6, 0, 0)
                    if cell.S:
                        self[x, y+1] = self.get_tile(x, y+1, 6, 0, 0)
            
            self.spawn = (2, 2)

            self[self.WIDTH-3, self.HEIGHT-2] = self.get_tile(self.WIDTH-3, self.HEIGHT-2, 10, 0, 0,)
            self[self.WIDTH-2, self.HEIGHT-3] = self.get_tile(self.WIDTH-2, self.HEIGHT-3, 10, 0, 0,)
            fond_moulin: ElaborateConnected = self.get_tile(self.WIDTH-1, self.HEIGHT-1, 7, 0, 1)
            fond_moulin.top = 1
            fond_moulin.left = 1
            fond_moulin.right = 0
            fond_moulin.bottom = 0
            self[self.WIDTH-1, self.HEIGHT-1] = Tile(
                self.WIDTH-1, self.HEIGHT-1,
                11, 0,
                self,
                fond_moulin,
            )
            self.update_all()
        elif False:
            self.background = 1
            self.WIDTH = width
            self.HEIGHT = height
            self.map = [
                [
                    self.get_tile(x, y, 0) for x in range(self.WIDTH)
                ] for y in range(self.HEIGHT)
            ]
    
    def __getitem__(self, coords:Tuple[Union[int, float], Union[int, float]]) -> Tile:
        """Retourne la tuile au coordonnées indiquées
        Exemple : map[0, 1] retourne la tuile située aux coordonnées x=0 et y=1
        """
        x, y = coords
        x, y = int(x), int(y)
        if x >= 0 and y >= 0 and x < len(self.map[0]) and y < len(self.map):
            return self.map[y][x]
        else:
            return self.get_tile(x, y, self.background, 0)
    
    def __setitem__(self, coords: Tuple[int, int], value: Tile) -> None:
        """Met à jour la tuile aux coordonnées indiquées par la valeur passée en paramètre
        Exemple : map[0, 1] = map.get_tile(0, 1, 0) remplacera la tuile située en x=0 et y=1 par de l'herbe
        """
        x, y = coords
        if x >= 0 and y >= 0 and x < len(self.map[0]) and y < len(self.map):
            self.map[y][x] = value
        
    def update_all(self) -> None:
        """Met à jour toutes les tuiles de la carte"""
        for row in self.map:
            for tile in row:
                tile.update()
    
    def render(self) -> None:
        """Traite le rendu du monde
        Cette fonction affiche sur l'écran de élément parent les tuiles affichables
        """
        self.animation_state += 1
        for y in range(int(self.parent.camera_y)-8, int(self.parent.camera_y)+10):
            for x in range(int(self.parent.camera_x)-11, int(self.parent.camera_x)+12):
                self[x, y].render(self.parent.screen)
            
    def get_tile(
        self,
        x: int,
        y: int,
        type: int,
        data: int = 0,
        background_type: Optional[int] = None,
        background_data:Optional[int]=0,
        force: Tile = None,
        force_background: Tile = None
    ) -> Tile:
        """Retourne la tuile construite avec la bonne classe pour les informations données
        
        Attributes
        ----------
        x: int
            La coordonnée `x` de la future tuile
        y: int
            La coordonnée `y` de la future tuile
        type: int
            Le type de la tuile (influence sur la classe du constructeur)
        data: int = 0
            Les données de la tuile (influence l'affichage comme la couleur par exemple)
        background_type: Optional[int] = None
            Si la tuile a un fond, son type est spécifié ici
        background_data: Optional[int] = 0
            Si la tuile a un fond, la donnée du fond est spécifiée ici
        force: Tile = None
            Cet argument est utilisé comme constructeur forcé de la tuile si il n'est pas nul
        force_background: Tile = None
            Cet argument est utilisé comme constructeur forcé du fond de la tuile si il n'est pas nul
        
        Returns
        -------
        Tile
            La tuile créée
        """
        if force is not None:
            cls = force
        else:
            cls = get_type(type)
        if background_type is not None:
            background: Optional[Tile] = self.get_tile(x, y, background_type, background_data, force=force_background)
        else:
            background = None
        return cls(x, y, type, data, self, background)
    
    def on_message(self, payload:Payload, discord: Discord) -> None:
        """Traite un message reçu sur le channel 2 (channel de mises à jour du monde)
        """
        if payload.type == World.get:
            if payload.data == WorldType.all:
                discord.send_message(
                    Channels.world_update.value,
                    Payload(
                        World.update.value,
                        [
                            WorldType.all.value,
                            self.to_dict(),
                        ]
                    )
                )
        elif payload.type == World.update:
            if payload.data[WorldKey.type] == WorldType.all:
                self.load_dict(payload.data[WorldKey.data.value])
    
    def query(self, discord: Discord) -> None:
        discord.send_message(
            Channels.world_update.value,
            Payload(
                World.get.value,
                WorldType.all.value
            )
        )
        
    @property
    def camera_x(self) -> int:
        """Retourne la coordonnée x actuelle de la caméra (celle du parent)"""
        return self.parent.camera_x
    
    @property
    def camera_y(self) -> int:
        """Retourne la coordonnée y actuelle de la caméra (celle du parent)"""
        return self.parent.camera_y
    
    @property
    def animation_state(self) -> int:
        """Retourne l'index de texture actuel général pour tout le jeu"""
        return self.parent.texture_index
    
    @animation_state.setter
    def animation_state(self, value: int) -> None:
        """Paramètre l'index de texture général sur la valeur donnée"""
        self.parent.texture_index = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Retourne le status actuel de la classe pour le sérialisateur"""
        map = []
        for row in self.map:
            dict_row = []
            for tile in row:
                dict_row.append(tile.to_dict())
            map.append(dict_row)
        state = {
            "map": map,
            "spawn": self.spawn,
        }
        return state
    
    def load_dict(self, dict: Dict[str, Any]) -> None:
        """Charge un fichier json dans l'instance actuelle.
        Cette fonction est utilisée pour charger le monde d'une partie
        multijoueur.
        """
        map = []
        map_to_load = dict["map"]
        for row in map_to_load:
            loading_row = []
            for tile in row:
                loading_row.append(Tile.from_dict(tile, self.parent))
            map.append(loading_row)
        self.spawn = dict.get("spawn", (0, 0))
        self.map = map
    
    def set_parent(self, parent):
        """Paramètre le parent de la classe et des enfants (les tuiles) pour
        correspondre aux informations données"""
        self.parent = parent
    
    def allow_move(self, x: int, y: int) -> bool:
        """Retourne si le joueur a le droit de marcher sur la tuile aux
        coordonnées `x` , `y`
        
        Attributes
        ----------
        x: int
            La coordonnée `x` du bloc
        y: int
            La coordonnée `y` du bloc
        
        Returns
        -------
        bool
            Si le joueur a le droit de marcher sur la tuile ou non
        """
        return not self[x, y].hitbox