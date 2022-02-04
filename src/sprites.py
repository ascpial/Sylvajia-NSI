from __future__ import annotations
from typing import Dict, List, Optional

import os.path
import json

import pygame
import pygame.image
import pygame.surface

IMAGE_PATH = "./data/images"

with open("./data/textures.json") as file:
    index = json.load(file)

def get_path(image_path) -> str:
    return os.path.join(IMAGE_PATH, image_path)

cache = {}

def load_image(name: str) -> pygame.surface.Surface:
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

    def __init__(self, name) -> None:
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
    
    def image(self, data=0, map_animation_state=0, x: int = 0, y: int = 0) -> pygame.surface.Surface:
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

def get_image(name) -> Image:
    if name not in cache:
        cache[name] = Image(name)
    return cache[name]

class Sprite:

    sprite:Image

    def __init__(self, name, data=0) -> None:
        self.sprite = get_image(name)
        self.x=0
        self.y=0
        self.data = data
    
    def center_at(self, x, y) -> None:
        self.x = x - self.sprite.image(self.data).get_width() // 2
        self.y = y - self.sprite.image(self.data).get_height() // 2
    
    def blit(self, surface:pygame.Surface, animation_state_:int=0, x:int = 0, y: int = 0) -> None:
        surface.blit(self.sprite.image(self.data, animation_state_, x, y), (self.x, self.y))

# pour les données des chemins (textures connectées) :
# 2**0 : haut
# 2**1 : bas
# 2**2 : gauche
# 2**3 : droite