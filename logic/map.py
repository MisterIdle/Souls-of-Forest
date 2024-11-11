import logic.entities as e
import logic.items as i
import logic.utils as u
import logic.combat as c
import logic.loop as l
import logic.save as s

class Map:
    current_map = None
    current_map_name = None
    all_maps = {}

    def __init__(self, map_data, tiles_data, map_name):
        self.map_name = map_name
        self.map_data = map_data
        self.tiles_data = tiles_data

        self.tile_items = {}
        self.tile_entities = {}
        self.tile_teleporters = {}

        self.load_map()

    def get_data(self):
        return {
            "name": self.map_name,
            "tiles": self.map,
            "entities": [
                entity.get_data() for entities in self.entities.values() for entity in entities
            ],
            "items": [
                item.get_data() for items in self.items.values() for item in items
            ],
            "teleporters": [
                {
                    "position": position,
                    "destination": teleporter["destination"],
                    "destination_coords": teleporter["destination_coords"]
                }
                for position, teleporter in self.teleporters.items()
            ]
        }

    def load_map(self):
        self.map = self.create_map()
        self.entities = self.create_entities(self.tile_entities)
        self.items = self.create_items(self.tile_items)
        self.teleporters = self.create_teleporters(self.tile_teleporters)

    def load_new_map(self, map_name, player_position):
        new_map = Map.get_map(map_name)
        if new_map is None:
            print(f"Error: Map {map_name} is not loaded.")
            return
        
        self.current_map = new_map
        self.current_map_name = map_name
        l.player.position = player_position

        print(f"Player has been teleported to {map_name} at {player_position}.")
        l.game_map = new_map

    def create_map(self):
        tile_map = []
        for row in self.map_data['tiles']:
            tile_map.append([self.tiles_data[tile]["symbol"] for tile in row])
        return tile_map

    def create_entities(self, tile_entities):
        for entity_data in self.map_data['entities']:
            entity_name = entity_data['name']
            entity_position = tuple(entity_data['position'])
            entity_quantity = entity_data.get('quantity', 1)
            entity_class = e.get_class_from_name(entity_name)

            for _ in range(entity_quantity):
                if entity_position not in tile_entities:
                    tile_entities[entity_position] = []

                entity = entity_class()
                entity.position = entity_position
                tile_entities[entity_position].append(entity)
        return tile_entities

    def create_items(self, tile_items):
        for item_data in self.map_data['items']:
            item_name = item_data['name']
            item_position = tuple(item_data['position'])
            item_class = i.get_class_from_name(item_name)

            if item_position not in tile_items:
                tile_items[item_position] = []
            item = item_class()
            item.position = item_position
            tile_items[item_position].append(item)
        return tile_items
    
    def create_teleporters(self, tile_teleporters):
        for teleporter_data in self.map_data['teleporters']:
            teleporter_position = tuple(teleporter_data['position'])
            teleporter_destination = teleporter_data['destination']
            teleporter_destination_coords = tuple(teleporter_data['destination_coords'])

            tile_teleporters[teleporter_position] = {
                "destination": teleporter_destination,
                "destination_coords": teleporter_destination_coords
            }
        return tile_teleporters

    def load_all_maps():
        for map_name, map_data in u.map_data.items():
            tiles_data = u.tiles_data
            map_instance = Map(map_data, tiles_data, map_name)
            Map.all_maps[map_name] = map_instance
            print(f"Map {map_name} loaded.")

    def get_map(map_name):
        return Map.all_maps.get(map_name)

    def remove_entity(self, entity):
        if entity.position in self.entities:
            self.entities[entity.position].remove(entity)
            print(f"Entity {entity.name} removed from tile {entity.position}.")
        else:
            print(f"Entity {entity.name} not found at tile {entity.position}.")


    def check_for_entity_collision(self, player_position):
        if player_position in self.entities:
            entities_at_position = self.entities[player_position]
            for entity in entities_at_position:
                combat = c.Combat(l.player, entity)
                combat.start_combat()

    def check_for_teleporter(self, player_position):
        if player_position in self.teleporters:
            teleporter = self.teleporters[player_position]
            destination_map_name = teleporter["destination"]
            destination_coords = teleporter["destination_coords"]

            print(f"Teleporting to {destination_map_name} at {destination_coords}.")
            self.load_new_map(destination_map_name, destination_coords)

            l.explored_maps[self.current_map_name] = self.current_map

    def show_items_on_tile(self, player_position):
        if player_position in self.items:
            items_at_position = self.items[player_position]
            for item in items_at_position:
                print(f"I see {item.name} on the ground.")
            print("[P] Pick up item\n")

    def pick_up_item(self, player_position):
        if player_position in self.items:
            items_at_position = self.items[player_position]
            for item in items_at_position:
                print(f"Player picked up {item.name}.")

    def drop_item(self, item):
        if item.position not in self.items:
            self.items[item.position] = []
        self.items[item.position].append(item)
        print(f"Item {item.name} added to tile {item.position}.")

    def is_move_valid(self, new_position):
        x, y = new_position
        if 0 <= x < len(self.map) and 0 <= y < len(self.map[0]):
            tile_symbol = self.map[x][y]
            tile = next(t for t in self.tiles_data.values() if t["symbol"] == tile_symbol)
            return not tile["blocksMovement"]
        return False
    
    def map_display(self, player_position=None):
        for x, row in enumerate(self.map):
            for y, tile_symbol in enumerate(row):
                position = (x, y)
                if position == player_position:
                    print(u.entities_data["player"]["symbol"], end=" ")
                elif position in self.items and self.items[position]:
                    print("L", end=" ")
                elif position in self.teleporters:
                    print("T", end=" ")
                elif position in self.entities and self.entities[position]:
                    print(self.entities[position][0].symbol, end=" ")
                else:
                    print(tile_symbol, end=" ")
            print()

    def map_compass(self, player_position):
        x, y = player_position
        compass = {
            "North": (x - 1, y),  # North
            "West": (x, y - 1),  # West
            "Est": (x, y + 1),  # East
            "South": (x + 1, y)   # South
        }

        for direction, position in compass.items():
            if self.is_move_valid(position):
                tile_symbol = self.map[position[0]][position[1]]
                tile_data = self.tiles_data[tile_symbol]
                if position in self.teleporters:
                    teleporter = self.teleporters[position]
                    destination = teleporter["destination"]
                    print(f"{direction}: Travel to {destination}")
                else:
                    print(f"{direction}: {tile_data['name']}")
            else:
                print(f"{direction}: Dense forest")


            