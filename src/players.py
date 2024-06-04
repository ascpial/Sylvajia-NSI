from __future__ import annotations
from typing import Dict, List, Optional, TYPE_CHECKING, Tuple

import time

import pygame
import pygame.image
from pygame.surface import Surface

from .sprites import Sprite

if TYPE_CHECKING:
    from .game import Pygame

MOVE_INTERVAL = 0.15

class Transition:
    def __init__(
        self,
        begin: int,
        end: int,
        duration: float
    ) -> None:
        """Créé un objet de transition utilisé pour rendre plus agréable à voir
        le déplacement d'un joueur.
        Une transition n'est disponible que sur un axe, et plusieurs
        transitions sont nécessaires pour gérer les deux dimensions.
        
        Attributes
        ----------
        begin: int
            Le point sur lequel commencer la transition
        end: int
            Le point sur lequel finir la transition
        duration: float
            La durée de la transition
        """
        self.begin = begin
        self.end = end
        self.value = self.begin
        self.start_time = time.time()
        self.end_time = self.start_time + duration
        self.duration = duration
    
    @property
    def done(self) -> bool:
        """Retourne True si la transition est finie
        
        Returns
        -------
        bool
            Le booléen indiquant si la transition est finie ou non
        """
        return time.time() >= self.end_time

    def get_state(self) -> float:
        """Retourne le stade actuel de la transition
        
        Returns
        -------
        float
            Le point actuel de la transition
        """
        act_time = time.time()
        if act_time >= self.end_time:
            return 1
        return (act_time-self.start_time) / self.duration
    
    def update(self) -> None:
        """Met à jour la valeur de la transition
        """
        if time.time() >= self.end_time:
            self.value = self.end
        self.value = self.begin + (self.end-self.begin)*self.get_state()

class Coords:
    coords: List[float, float]
    transition: List[Optional[Transition]]

    def __init__(self, x: int = 0, y: int = 0) -> None:
        """Initialise le joueur
        
        Attributes
        ----------
        x: int = 0
            La coordonnée x du point sur lequel créer le joueur
        y: int = 0
            La coordonnée x du point sur lequel créer le joueur
        """
        self.coords = [x, y]
        self.transition = [None, None]
    
    @property
    def x(self) -> float:
        if self.transition[0] is None:
            return self.coords[0]
        else:
            return self.transition[0].value
    @x.setter
    def x(self, value: int) -> None:
        if (self.transition[0] is None) or self.transition[0].done:
            if self.transition[0] is not None: # prévient les rollback
                self.coords[0] = self.transition[0].value
            self.transition[0] = Transition(
                self.coords[0],
                value,
                MOVE_INTERVAL,
            )
    
    @property
    def y(self) -> float:
        if self.transition[1] is None:
            return self.coords[1]
        else:
            return self.transition[1].value
    @y.setter
    def y(self, value: int) -> None:
        if (self.transition[1] is None) or self.transition[1].done:
            if self.transition[1] is not None: # prévient les rollback
                self.coords[1] = self.transition[1].value
            self.transition[1] = Transition(
                self.coords[1],
                value,
                MOVE_INTERVAL,
            )
        
    def update(self) -> None:
        """Met à jour les transition du joueur
        """
        for i, transition in enumerate(self.transition):
            if transition is not None:
                transition.update()
                if transition.done:
                    self.coords[i] = self.transition[i].value
                    self.transition[i] = None

    def real_coords(self) -> Tuple[int]:
        """Cette fonction retourne les réelles coordonnées, en ignorant la valeur de l'animation.
        
        Returns
        -------
        Tuple[int]
            Les réelles coordonnées
        """
        if self.transition[0] is not None:
            x = self.transition[0].end
        else:
            x = self.coords[0]
        if self.transition[1] is not None:
            y = self.transition[1].end
        else:
            y = self.coords[1]
        return (x, y)

class Player:
    """Cette classe contient un joueur et procède à son affichage."""
    x: int
    y: int
    id: int

    color_: int = 0

    name: Optional[str] = None
    rendered_name: Optional[Surface] = None

    def __init__(self, id: int, parent: Pygame, x: int = 0, y: int = 0) -> None:
        """Créé le joueur en fonction des arguments donnés.
        
        Attributes
        ----------
        id: int
            L'ID du joueur utilisé dans les requêtes pour l'identifier
        parent: Pygame
            Le parent utilisé pour connaître les coordonnées de la caméra par exemple
        x: int = 0
            La coordonnée `x` du joueur
        y: int = 0
            La coordonnée `y` du joueur
        """
        self.parent = parent
        self.id = id
        self.coords = Coords(x, y)
        self.color = 0
        self.name = ""
        self.rendered_name = self.parent.small_font.render(
            self.name,
            True,
            0x000000
        )
    
    @property
    def color(self) -> int:
        return self.color_

    @color.setter
    def color(self, value: int) -> None:
        self.color_ = value
        self.sprite = Sprite("player", data=self.color)
    
    def render(self)-> None:
        """Affiche le joueur sur l'écran (`self.parent.screen`)"""
        screen:pygame.Surface = self.parent.screen
        x = (self.x - self.parent.camera_x) * 32 + self.parent.screen.get_width()//2
        y = (self.y - self.parent.camera_y) * 32 + self.parent.screen.get_height()//2
        self.sprite.center_at(x, y)
        if self.rendered_name is not None:
            x -= self.rendered_name.get_width()//2
            y -= 30
            screen.blit(self.rendered_name, (x, y))
        self.sprite.blit(screen)
    
    def move_by(self, offset_x: int = 0, offset_y: int = 0, check_move: bool = True) -> bool:
        """Déplace le joueur avec les coordonnées indiquées.
        
        Attributes
        ----------
        offset_x: int = 0
            La coordonnée relative par rapport à x
        offset_y: int = 0
            La coordonnée relative par rapport à y
        check_move: bool = True
            Si `check_mode`vaut `True`, alors le joueur vérifie si le mouvement est possible.
            Pour cela, il regarde si la tuile aux coordonnées indiquées a une hitbox, et ne fait pas de mouvement si c'est le cas.
        
        Returns
        -------
        bool
            Indique si le joueur a été déplacé ou non
        """
        x, y = self.coords.real_coords()
        new_x = x + offset_x
        new_y = y + offset_y
        check = self.parent.map.allow_move(new_x, new_y)
        if check or not check_move:
            if offset_x != 0:
                if self.coords.transition[0] is None or self.coords.transition[0].done:
                    self.x = new_x
            if offset_y != 0:
                if self.coords.transition[1] is None or self.coords.transition[1].done:
                    self.y = new_y
        return check
    
    @property
    def x(self) -> float:
        return self.coords.x
    @x.setter
    def x(self, value: int) -> None:
        if self.coords.transition[0] is None or self.coords.transition[0].done:
            self.coords.x = value
    
    @property
    def y(self) -> float:
        return self.coords.y
    @y.setter
    def y(self, value: int) -> None:
        if self.coords.transition[1] is None or self.coords.transition[1].done:
            self.coords.y = value
    
    def update_animation(self) -> None:
        self.coords.update()

class Players:
    """Cette classe contient tout les joueurs connectés au monde actuel.
    C'est un équivalent de dictionnaire amélioré.
    """
    parent: Pygame
    players: Dict[int, Player] = {}
    player: Optional[Player]

    def __init__(self, parent: Pygame) -> None:
        """Initialise la classe (mais pas les données)
        
        Attributes
        ----------
        parent: Pygame
            Le parent de la classe (l'instance du jeu)
        """
        self.parent = parent
        self.player_id = None
        self.player = None
    
    def init(self) -> None:
        """Cette fonction initialise le joueur.
        """
        self.player_id = 0
        self.new(self.player_id)
        self.player.color = 1
    
    def __getitem__(self, player_id: int) -> Player:
        """Cette fonction retourne un joueur en fonction d'un identifiant
        
        Attributes
        ----------
        player_id: int
            L'ID du joueur à récupérer
        
        Returns
        -------
        Player
            Le joueur
        """
        return self.players[player_id]
    
    def new(self, player_id: int) -> None:
        """Cette fonction créé un nouveau joueur et l'ajoute dans le dictionnaire
        
        Attributes
        ----------
        player_id: int
            L'identifiant du joueur à créer dans le dictionnaire
        """
        if not player_id in self.players:
            self.players[player_id] = Player(
                player_id,
                self.parent,
                self.parent.map.spawn[0],
                self.parent.map.spawn[1],
            )
            if player_id == self.player_id:
                self.player = self[player_id]
    
    def remove(self, player_id: int) -> None:
        """Supprimes un joueur du dictionnaire.
        
        Attributes
        ----------
        player_id: int
            L'identifiant du joueur à supprimer du dictionnaire
        """
        if player_id in self.players:
            del self.players[player_id]
    
    def render(self) -> None:
        """Effectue l'affichage de tout les joueurs.
        """
        for player in self.players.values():
            player.update_animation()
            player.render()
  
    def reset(self) -> None:
        """Cette fonction réinitialise tout les joueurs.
        """
        self.players = {}
        self.player = None
        self.color = 0
