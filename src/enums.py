"""Ce fichier contient les constantes du projet.
Ce sont des nombres qui sont utilisé par le programme pour identifier certaines choses notamment dans les playloads,
afin de transmettre les informations.
"""

from __future__ import annotations

from enum import IntEnum

class Channels(IntEnum):
    player_pos = 1
    world_update = 2

class PlayerPos(IntEnum):
    update = 0

class PlayerPosKey(IntEnum):
    pos_x = 0
    pos_y = 1
    user_id = 2

class World(IntEnum):
    get = 0
    update = 1

class WorldKey(IntEnum):
    type = 0
    data = 1

class WorldType(IntEnum):
    all = 0

class Blocs(IntEnum):
    grass=0
    sea=1
    path=2
    moulin=3
    gravel_path=4
    river=5
    muraille=6
    border=7
    bridge=8
    stone_bridge=9
    entrance=10
    lake=12