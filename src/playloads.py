from __future__ import annotations
from typing import Any, Literal, Optional

import json

# class Playload:
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
#     def from_str(cls, string: str) -> Playload:
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
#     def from_bytes(cls, bytes: bytes) -> Playload:
#         return cls.from_str(bytes.decode("utf8"))

class Playload:
    peer_id: Optional[int]
    channel_id: Optional[int]

    def __init__(self, type: int, data: Any) -> None:
        self.type = type
        self.data = data
    
    def __str__(self) -> str:
        state = [
            self.type,
            self.data
        ]
        return json.dumps(state)
    
    @classmethod
    def from_str(cls, string: str) -> Playload:
        decoded_data = json.loads(string)
        type = decoded_data[0]
        data = decoded_data[1]

        return cls(type, data)

    @classmethod
    def from_bytes(cls, bytes: bytes) -> Playload:
        return cls.from_str(bytes.decode("utf8"))
