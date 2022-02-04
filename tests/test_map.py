from random import randint
from src.map import Map, Connected, Tile, OneWayConnected, ElaborateConnected, get_type

class TestMap:

    def test_get_type(self):
        for check, tests in [
            (Connected, [2, 4, 5, 6]),
            (ElaborateConnected, [7]),
            (OneWayConnected, [8, 9, 10]),
            (Tile, [0, 1, 3])
        ]:
            for test in tests:
                type = get_type(test)
                if not type == check:
                    raise f"Le résultat de src.map.get_type avec type={test} devrait être {check}, pas {type}"
    
    def get_test_map(self) -> Map:
        self.height, self.width = 15, 15
        # On passe None en parent ce qui ne pose pas de problèmes tant qu'on n'appelle pas map.__getstate__
        try:
            map = Map(
                parent=None,
                height=self.height,
                width=self.width,
                generate_maze=False
            )
        except Exception as e:
            raise f"Impossible de construire le monde : {e.__class__.__name__}: {e}"
        return map
    
    def test_map_get_tile(self):
        map = self.get_test_map()
        for type in range(11):
            x, y = randint(0, self.height-1), randint(0, self.width-1)
            map.get_tile(
                x, y,
                type,
            )
    
    def test_dict_conversion(self):
        map = self.get_test_map()
        for type in range(11):
            x, y = randint(0, self.height-1), randint(0, self.width-1)
            tile = map.get_tile(
                x, y,
                type,
            )
            to_check = tile.from_dict(tile.to_dict(), None)
            assert tile.x==to_check.x
            assert tile.y==to_check.y
            assert tile.type==to_check.type
        
    def test_connected_data(self):
        map = self.get_test_map()
        # On créé un carré de 3*3 de chemins pour tester toutes les combinaisons

        for y in range(3):
            map[0, y+2] = map.get_tile(0, y+2, 2)
            for x in range(3):
                map[x+2, y+2] = map.get_tile(x+2, y+2, 2)
        for x in range(3):
            map[x+2, 0] = map.get_tile(x+2, 0, 2)
        map.update_all()

        assert map[0,3].data==3
        assert map[3,0].data==12
        
        assert map[2,2].data==10
        assert map[3,2].data==14
        assert map[4,2].data==6
        assert map[2,3].data==11
        assert map[3,3].data==15
        assert map[4,3].data==7
        assert map[2,4].data==9
        assert map[3,4].data==13
        assert map[4,4].data==5