from __future__ import annotations
from typing import Any, Literal, Optional

###
# Format
#
# type : 1 octet (0-255)
# user_id (detrminated by the server user) : 2 (0 -> 65536)
# ensuite le reste des infos
# pour chaque partie, il y a un octet qui détermine le type de la donnée
# 0: un nombre sur un octet non signé
# 1: un nombre sur un octet signé
# 2: un nombre sur deux octets non signé
# 3: un nombre sur deux octets signé
# 20 (20 -> custom data): 2*4 octets signés qui indique x et y à la suite (position en 8 octets)
#
###

class Playload:
    type: int
    user_id: int

    def __init__(self, type = 0, user_id = 0):
        self.type = type
        self.user_id = user_id
    
    def to_bytes(self):
        data = bytearray()

        # adding type to the bytearray (1 octet not signed)
        data.extend(self.type.to_bytes(1, byteorder="little", signed=False))

        # adding user_id to the bytearray (2 octets not signed)
        data.extend(self.user_id.to_bytes(2, byteorder='little'))

        return bytes(data)
    
    @classmethod
    def from_bytes(cls, bytes) -> Playload:
        instance = cls.__new__(cls)
        bytes = bytearray(bytes)
        instance.type = bytes.pop(0)

if __name__ == "__main__":
    test = Playload(0, 0)
    print(test.to_bytes())
    test = Playload(1, 16)
    print(test.to_bytes())
    test = Playload(56, 1256)
    print(test.to_bytes())