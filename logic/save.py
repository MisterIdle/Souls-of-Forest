import json
import os
import logic.map as m
import logic.entities as e
import logic.utils as u
import logic.loop as l

class Save:
    def __init__(self, filename="savegame.json"):
        self.filename = filename

    def save_game(self, explored_maps, player):
        data = {
            "player": player.get_data(),
            "explored_maps": {
                map_name: map_instance.get_data()
                for map_name, map_instance in explored_maps.items()
            }
        }

        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    def load_game(self):
        if not os.path.exists(self.filename):
            print("No save game found")
            return None, None

        with open(self.filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

        m.Map.load_all_maps()
        print("Map loaded")

        player = e.Player(data["player"])
        print("Player loaded")

        explored_maps = {
            map_name: m.Map(map_data=map_data, tiles_data=u.tiles_data, map_name=map_name)
            for map_name, map_data in data["explored_maps"].items()
        }

        l.game_map = explored_maps[player.current_map]
        print("Maps loaded")

        return explored_maps, player
        