from __future__ import annotations
from typing import Any, Literal, Optional

import json

# class Payload:
#     peer_id: Optional[int]
#     channel_id: Optional[int]
#     #user_id: Optional[int]

#     def __init__(self, type: int, data: Any) -> None:
#         self.type = type
#         self.data = data
    
#     def __str__(self) -> str:
#         def to_str(item) -> str:
#             if type(item) == [int, float]:
#                 return str(item)
#             elif type(item) in [list, tuple]:
#                 return "/".join([to_str(i) for i in item])
#             else:
#                 return item
        
#         return f"{to_str(self.type)}:{to_str(self.data)}"
    
#     @classmethod
#     def from_str(cls, string: str) -> Payload:
#         type, data = string.split(":")
#         type = int(type)
#         def to_item(string: str) -> Any:
#             try:
#                 return int(string)
#             except:
#                 try:
#                     return float(string)
#                 except:
#                     if "/" in string:
#                         return [to_item(i) for i in string.split("/")]
#                     else:
#                         return string

#         data = to_item(data)
    
#         return cls(type, data)
    
#     @classmethod
#     def from_bytes(cls, bytes: bytes) -> Payload:
#         return cls.from_str(bytes.decode("utf8"))

class Payload:
    peer_id: Optional[int]
    channel_id: Optional[int]

    def __init__(self, type: int, data: Any) -> None:
        """Initialise la charge utile.
        Les données peuvent être de n'importe quel type pour peu qu'il soit
        sérialisable par le module json.
        
        Attributes
        ----------
        type: int
            Le type de payload à envoyer
        data: Any
            La charge utile à inclure dans le paquet
        """
        self.type = type
        self.data = data
    
    def __str__(self) -> str:
        """Transforme la charge utile en chaîne de caractères utilisable
        
        Returns
        -------
        str
            La chaîne de caractère utilisable en tant que charge utile
        """
        state = [
            self.type,
            self.data
        ]
        return json.dumps(state)
    
    @classmethod
    def from_str(cls, string: str) -> Payload:
        """Retourne la charge utile à partir d'un chaîne de caractères
        
        Attributes
        ----------
        string: str
            La chaîne à partir de laquelle récupérer la charge utile
        
        Returns
        -------
        Payload
            La classe représentant la charge utile
        """
        decoded_data = json.loads(string)
        type = decoded_data[0]
        data = decoded_data[1]

        return cls(type, data)

    @classmethod
    def from_bytes(cls, bytes: bytes) -> Payload:
        """Retourne la charge utile à partir de données binaires
        Note : cette fonction transforme les données binaire en chaîne de
        caractère et retourne `Payload.from_str` avec comme argument les
        données binaire encodées en utf-8.
        
        Attributes
        ----------
        bytes: bytes
            Les données binaires à partir desquels récupérer la charge utile
        
        Returns
        -------
        Payload
            La classe représentant la charge utile
        """
        return cls.from_str(bytes.decode("utf8"))
