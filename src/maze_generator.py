from __future__ import annotations
from typing import List, Literal, NewType, Optional, Tuple

import random


class Cell:
    """Cette classe représente une case d'un labyrinthe.
    Elle est utilisée pour savoir quels côté d'une case sont murés.
    """
    zone: List[Cell]

    def __init__(self, x: int, y: int, parent: Maze) -> None:
        self.parent = parent
        self.x = x
        self.y = y
        self.N = True
        self.S = True
        self.E = True
        self.O = True
    
    def get_wall(self, value: Literal[1, 2, 3, 4]) -> bool:
        """Cette fonction retourne True si un mur est présent à l'orientation
        
        Attributes
        ----------
        value: Literal[1, 2, 3, 4]
            L'orientation demandée
            Les orientations par nombres sont :
              2
            1   3
              4
        
        Returns
        -------
        bool
            Indique si un mur est présent où non
        """
        if value == 1:
            return self.O
        elif value == 2:
            return self.N
        elif value == 3:
            return self.E
        elif value == 4:
            return self.S

    def get_side(self, value: Literal[1, 2, 3, 4]) -> Optional[Cell]:
        """Retourne la case voisine suivant l'orientation indiquée
        
        Attributes
        ----------
        value: Literal[1, 2, 3, 4]
            L'orientation
            Les orientations sont les suivantes :
              2
            1   3
              4
        
        Returns
        -------
        Optional[Cell]
            La cellule présente à l'orientation indiquée si elle existe
            (par exemple si la case est sur un bord cette fonction retourne None)
        """
        if value == 1:
            if self.x > 0:
                return self.parent.cells[self.y][self.x-1]
        elif value == 2:
            if self.y > 0:
                return self.parent.cells[self.y-1][self.x]
        elif value == 3:
            if self.x < self.parent.width-1:
                return self.parent.cells[self.y][self.x+1]
        elif value == 4:
            if self.y < self.parent.height-1:
                return self.parent.cells[self.y+1][self.x]
        return None
    
    def remove_wall(self, cell: Cell) -> None:
        """Cette fonction supprimes le mur en commun avec la cellule.
        Si la cellule n'a aucun mur en commun avec l'autre, alors cette fonction
        ne fait rien
        
        Attributes
        ----------
        cell: Cell
            La cellule à vérifier
        """
        if self.get_side(1) == cell:
            self.O = False
        elif self.get_side(2) == cell:
            self.N = False
        elif self.get_side(3) == cell:
            self.E = False
        elif self.get_side(4) == cell:
            self.S = False

class Maze:
    cells: List[List[Cell]]
    zones: List[List[Cell]]

    def __init__(self, width: int, height: int) -> None:
        """Prépare le labyrinthe pour pouvoir être généré avec `Maze.generate`
        
        Attributes
        ----------
        width: int
            La largeur du labyrinthe.
        height: int
            La hauteur du labyrinthe.
        """
        self.width = width
        self.height = height
        self.cells = [
            [Cell(x, y, self) for x in range(self.width)]
            for y in range(self.height)
        ]
        self.zones = []
        for row in self.cells:
            for cell in row:
                self.zones.append([cell])
        for zone in self.zones:
            zone[0].zone = zone

    def generate(self) -> None:
        """Cette fonction génère le labyrinthe suivant les paramètres indiqués
        (hauteur et largeur)
        """
        while len(self.zones) > 1:
            x, y = (random.randint(0, self.width-1), random.randint(0, self.height-1))
            cell = self.cells[y][x]
            side = random.randint(1, 4)
            neighbour = cell.get_side(side)
            if neighbour is not None and cell.get_wall(side) and neighbour not in cell.zone:
                self.fusionner(cell, neighbour)
    
    def fusionner(self, cell_1: Cell, cell_2: Cell) -> None:
        """Cette fonction fusionne deux cases (et leurs zones)
        dans une seule zone.
        Elle supprimes le mur en commun et fusionne les zones.
        
        Attributes
        ----------
        cell_1: Cell
        cell_2: Cell
            Les cellules à fusionner
        """
        new_zone = cell_1.zone + cell_2.zone
        cell_1.remove_wall(cell_2)
        cell_2.remove_wall(cell_1)
        cell_1_zone = cell_1.zone
        cell_2_zone = cell_2.zone
        self.zones.remove(cell_1.zone)
        self.zones.remove(cell_2.zone)
        for cell in cell_1_zone + cell_2_zone:
            cell.zone = new_zone
        self.zones.append(new_zone)

# Lancer ce script directement va lancer un test
if __name__ == "__main__":
    maze = Maze(5, 4)
    maze.generate()
    print(maze.cells)