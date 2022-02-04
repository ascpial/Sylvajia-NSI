from .enums import Channels, World, WorldKey, WorldType
from .playloads import Playload

class Request:
    def __init__(self, parent):
        self.parent = parent
    
    def get_playload(self, type, data) -> Playload:
        type = type.value()
        data_ = {}
        for key, 


    def world_get_background(self):
        playload = self.get_playload(
            World.get,
            
        )