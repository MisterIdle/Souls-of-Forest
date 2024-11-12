import logic.entities as e
import logic.items as i
import logic.utils as u
import logic.combat as c
import logic.loop as l
import logic.save as s
import logic.shop as sh

class Map:
    current_map = None
    current_map_name = None
    all_maps = {}

    def __init__(self, map_data, tiles_data, map_name):
        self.map_data = map_data
        self.map_name = map_name
        self.tiles_data = tiles_data
        self.tile_names = [tile["name"] for tile in tiles_data.values()]
        self.tile_descriptions = [tile["description"] for tile in tiles_data.values()]

        self.tile_items = {}
        self.tile_entities = {}
        self.tile_teleporters = {}
        self.tile_shop = {}

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
            ],
            "shops": [
                {
                    "position": position,
                    "name": shop["name"],
                }
                for position, shop in self.tile_shop.items()
            ]
        }
    
    def get_tile_name(self, position):
        x, y = position
        tile_symbol = self.map[x][y]
        return next(t["name"] for t in self.tiles_data.values() if t["symbol"] == tile_symbol)
    
    def get_tile_description(self, position):
        x, y = position
        tile_symbol = self.map[x][y]
        return next(t["description"] for t in self.tiles_data.values() if t["symbol"] == tile_symbol)
    
    def get_map_name(self):
        return self.map_name

    def load_map(self):
        self.map = self.create_map()
        self.entities = self.create_entities(self.tile_entities)
        self.items = self.create_items(self.tile_items)
        self.teleporters = self.create_teleporters(self.tile_teleporters)
        self.tile_shop = self.create_shop(self.tile_shop)

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
    
    def create_shop(self, tile_shop):
        for shop_data in self.map_data['shops']:
            shop_position = tuple(shop_data['position'])
            shop_name = shop_data['name']

            tile_shop[shop_position] = {
                "name": shop_name
            }
        return tile_shop

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
                combat = c.Combat(l.player, entity, l.game_map)
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
                print(f"Item {item.name} found at tile {item.position}.")

    def check_for_shop(self, player_position):
        if player_position in self.tile_shop:
            shop_data = u.shop_data[self.tile_shop[player_position]["name"]]
            shop_instance = sh.Shop(shop_data)
            shop_instance.open_shop()

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
    
    # Debug map
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
                elif position in self.tile_shop:
                    print("S", end=" ")
                elif position in self.entities and self.entities[position]:
                    print(self.entities[position][0].symbol, end=" ")
                else:
                    print(tile_symbol, end=" ")
            print()

    # SpellMap
    def map_display_spell(self, game_map, player_position):
        radius = 3
        x, y = player_position
        u.line()

        for i, row in enumerate(game_map.map):
            for j, tile_symbol in enumerate(row):
                if abs(i - x) + abs(j - y) <= radius:
                    position = (i, j)
                    if position == player_position:
                        print(u.entities_data["player"]["symbol"], end=" ")
                    else:
                        print(tile_symbol, end=" ")
                else:
                    print(" ", end=" ")
            print()
        u.line()

        print("Legend:")
        print("Player: @")
        for symbol, tile_data in game_map.tiles_data.items():
            print(f"{symbol}: {tile_data['name']}")

        u.wait()

    def map_compass(self, player_position):
        x, y = player_position
        compass = {
            "North": (x - 1, y),
            "West": (x, y - 1),
            "East": (x, y + 1),
            "South": (x + 1, y)
        }

        directions_info = {}

        for direction, position in compass.items():
            if self.is_move_valid(position):
                tile_symbol = self.map[position[0]][position[1]]
                tile_data = self.tiles_data[tile_symbol]
                if position in self.teleporters:
                    teleporter = self.teleporters[position]
                    destination = teleporter["destination"]
                    destination_name = u.map_data[destination]["name"]
                    directions_info[direction] = destination_name
                else:
                    directions_info[direction] = tile_data["name"]
            else:
                # Affiche quand même le nom de la tuile même si le mouvement n'est pas valide
                directions_info[direction] = "Obstacle"
        
        u.line()
        u.print_centered(f"=== Zone ===")
        u.line()
        destination = self.get_map_name()
        u.print_centered("Map: " + u.map_data[destination]["name"])
        u.print_centered("Zone: " + self.get_tile_name(player_position))
        u.print_centered("Description: " + self.get_tile_description(player_position))
        u.print_centered("Player Position: " + str(player_position))
        u.line()
        print()
        print()
        u.line()
        u.print_centered("=== Compass ===")
        u.line()
        u.print_centered(f"North")
        u.print_centered(directions_info["North"])
        u.print_both("West", "East")
        u.print_both(directions_info["West"], directions_info["East"])
        u.print_centered("South")
        u.print_centered(directions_info["South"])
        u.line()
        print()
        print()
            