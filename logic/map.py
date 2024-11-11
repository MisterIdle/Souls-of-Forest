import logic.entities as e
import logic.items as i
import logic.utils as u
import logic.combat as c
import logic.loop as l

class Map:
    current_map = None
    current_map_name = None
    all_maps = {}

    def __init__(self, map_data, tiles_data, map_name):
        self.map_name = map_name
        self.map_data = map_data
        self.tiles_data = tiles_data
        self.stats = {}
        
        self.tile_items = {}
        self.tile_entities = {}
        self.tile_teleporters = {}

        self.load_map()

    def load_map(self):
        self.map = self.create_map()
        self.entities = self.create_entities(self.tile_entities)
        self.items = self.create_items(self.tile_items)
        self.teleporters = self.create_teleporters(self.tile_teleporters)

    def load_new_map(self, map_name, player_position):
        new_map = Map.get_map(map_name)
        if new_map is None:
            print(f"Map {map_name} is not loaded.")
            return
        
        Map.current_map = new_map
        Map.current_map_name = map_name
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
        entities_at_position = self.entities.get(entity.position, [])
        if entity in entities_at_position:
            entities_at_position.remove(entity)
            if not entities_at_position:
                del self.entities[entity.position]

    def check_for_entity_collision(self, player_position):
        if player_position in self.entities:
            entities_at_position = self.entities[player_position]
            for entity in entities_at_position:
                combat = c.Combat(l.player, entity)
                combat.start_combat()
                if l.player.health <= 0:
                    l.player.die()
                    break
                if entity.health <= 0:
                    self.remove_entity(entity)
                    break

    def check_for_teleporter(self, player_position):
        if player_position in self.teleporters:
            teleporter = self.teleporters[player_position]
            destination_map_name = teleporter["destination"]
            destination_coords = teleporter["destination_coords"]

            print(f"Teleporting to {destination_map_name} at {destination_coords}.")
            self.load_new_map(destination_map_name, destination_coords)

    def show_items_on_tile(self, player_position):
        if player_position in self.items:
            items_at_position = self.items[player_position]
            for item in items_at_position:
                print(f"I see {item.name} on the ground.")

    def pick_up_item(self, player_position):
        if player_position in self.items:
            items_at_position = self.items[player_position]
            for item in items_at_position:
                print(f"Player picked up {item.name}.")
            del self.items[player_position]

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
    
    def display(self, player_position=None):
        for x, row in enumerate(self.map):
            for y, tile_symbol in enumerate(row):
                position = (x, y)
                if position == player_position:
                    print(u.entities_data["player"]["symbol"], end=" ")
                elif position in self.items and self.items[position]:
                    print("L", end=" ")
                elif position in self.teleporters:
                    print("T", end=" ")  # Symbole pour le téléporteur
                elif position in self.entities and self.entities[position]:
                    print(self.entities[position][0].symbol, end=" ")
                else:
                    print(tile_symbol, end=" ")
            print()