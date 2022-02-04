from __future__ import annotations
from typing import Dict, List, Optional

import os.path
import json

import pygame
import pygame.image
import pygame.surface

IMAGE_PATH = "./data/images"

with open("./data/textures.json") as file: # chargement des textures
    index = json.load(file)

def get_path(image_path: str) -> str:
    """Retourne le chemin du fichier relatif selon le chemin relatif de l'image
    Cette fonction ajoute `image_path` à `IMAGE_PATH`.
    
    Attributes
    ----------
    image_path: str
        Le chemin de l'image
    
    Returns
    -------
    str
        Le chemin complet
    """
    return os.path.join(IMAGE_PATH, image_path)

cache = {}

def load_image(name: str) -> pygame.surface.Surface:
    """Charge une image et retourne la surface correspondante.
    
    Attributes
    ----------
    name: str
        Le nom de l'image à charger
    
    Returns
    -------
    pygame.surface.Surface
        La surface pygame de l'image.
    """
    entire_path = get_path(name)
    if entire_path not in cache:
        image = pygame.image.load(entire_path)
        cache[entire_path] = image
        return image
    else:
        return cache[entire_path]

class Image:
    frames: List[pygame.surface.Surface]
    datas: Dict[int, pygame.surface.Surface]
    grid: List[pygame.surface.Surface]
    interval: Optional[int]

    def __init__(self, name: str) -> None:
        """Initialise l'image
        
        Attributes
        ----------
        name: str
            Le nom de l'image à charger
        """
        self.name = name
        self.type = index[name]["type"]
        self.default = load_image(index[name]["location"])
        if self.type == 0:
            self.frames = [self.default]
            self.datas = {}
            self.grid = []
            self.interval = None
        elif self.type == 1:
            self.frames = []
            self.datas = {}
            self.grid = []
            for image in index[name]["frames"]:
                self.frames.append(load_image(image))
            self.interval = index[name]["interval"]
        elif self.type == 2:
            self.frames = [self.default]
            self.datas = {}
            self.grid = []
            for data, image in index[name]["datas"].items():
                self.datas[int(data)] = load_image(image)
            self.interval = 0
        elif self.type == 3:
            self.frames = []
            self.datas = {}
            self.interval = None
            self.grid = []
            for image in index[name]["grid"]:
                self.grid.append(load_image(image))
    
    def image(
        self,
        data=0,
        map_animation_state=0,
        x: int = 0,
        y: int = 0,
    ) -> pygame.surface.Surface:
        """Retourne l'image correspondant au stade actuel à afficher.
        
        Attributes
        ----------
        data: int = 0
            La donnée de l'image (peut influer sur la forme d'un chemin…)
        map_animation_state: int = 0
            Le stade d'animation de la tuile (par exemple pour la mer)
        x: int = 0
            La coordonnée x de la tuile si applicable
            (pour les textures alternées)
        y: int = 0
            La coordonnée y de la tuile si applicable
            (pour les textures alternées)
        
        Returns
        -------
        pygame.surface.Surface
            La surface pygame correspondant à l'image
        """
        if self.type == 1:
            return self.frames[(map_animation_state//self.interval)%len(self.frames)-1]
        elif self.type == 2:
            if data in self.datas:
                return self.datas[data]
            else:
                return self.default
        elif self.type == 3:
            return self.grid[(x+y)%2]
        else:
            return self.default

cache:Dict[str,Image] = {}

def get_image(name: str) -> Image:
    """Retourne une image en la récupérant depuis le cache si disponible ou en
    chargeant la texture.
    
    Attributes
    ----------
    name: str
        Le nom de la texture à charger
    
    Returns
    -------
    Image
        L'image correspondant à la texture demandée
    """
    if name not in cache:
        cache[name] = Image(name)
    return cache[name]

class Sprite:

    sprite: Image

    def __init__(self, name: str, data=0) -> None:
        """Initialise un lutin.
        Cette classe est utilisée pour gérer facilement l'affichage d'une tuile
        à des coordonnées précises
        
        Attributes
        ----------
        name: str
            Le nom de la texture à charger
        data: int = 0
            La donnée par défaut de la texture à charger
        """
        self.sprite = get_image(name)
        self.x=0
        self.y=0
        self.data = data
    
    def center_at(self, x: int, y: int) -> None:
        """Centre la texture à un point sur l'écran en utilisant la taille
        de la texture
        
        Attributes
        ----------
        x: int
            La coordonnée `x` du point sur lequel centrer la texture
        y: int
            La coordonnée `y` du point sur lequel centrer la texture
        """
        self.x = x - self.sprite.image(self.data).get_width() // 2
        self.y = y - self.sprite.image(self.data).get_height() // 2
    
    def blit(self, surface:pygame.Surface, animation_state_:int=0, x:int = 0, y: int = 0) -> None:
        surface.blit(self.sprite.image(self.data, animation_state_, x, y), (self.x, self.y))

# pour les données des chemins (textures connectées) :
# 2**0 : haut
# 2**1 : bas
# 2**2 : gauche
# 2**3 : droite