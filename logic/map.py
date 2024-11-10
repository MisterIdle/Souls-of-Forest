import logic.entities as e
import logic.items as i
import logic.utils as u

class Map:
    current_map = None
    current_map_name = None

    def __init__(self, map_data, tiles_data, map_name):
        self.map_name = map_name
        self.map_data = map_data
        self.tiles_data = tiles_data

        self.map = self.create_map()
        self.entities = self.create_entities()
        self.items = self.create_items()

        self.current_map = self
        self.current_map_name = self.map_name

    def create_map(self):
        tile_map = []
        for row in self.map_data['tiles']:
            tile_map.append([self.tiles_data[tile]["symbol"] for tile in row])
        return tile_map

    def create_entities(self):
        entities = {}
        for entity_data in self.map_data['entities']:
            entity_name = entity_data['name']
            entity_position = tuple(entity_data['position'])
            entity_quantity = entity_data.get('quantity', 1)
            entity_class = e.get_class_from_name(entity_name)

            for _ in range(entity_quantity):
                if entity_position not in entities:
                    entities[entity_position] = []

                entity = entity_class()
                    
                entity.position = entity_position
                print(entity.position)

                entities[entity_position].append(entity)
                print(f"Entity {entity_name} created at {entity_position}.")

        return entities

    def create_items(self):
        items = {}
        for item_data in self.map_data['items']:
            item_name = item_data['name']
            item_position = tuple(item_data['position'])
            item_class = i.get_class_from_name(item_name)

            if item_position not in items:
                items[item_position] = []
            item = item_class()
            item.position = item_position
            items[item_position].append(item)
            print(f"Item {item_name} created at {item_position}.")
        return items

    def check_for_entity_collision(self, player_position):
        entities_at_position = self.entities.get(player_position, [])
        if entities_at_position:
            print(f"Player steps on {len(entities_at_position)} entities:")
            for entity in entities_at_position:
                if entity.name != "Player":
                    print(f"  {entity.name}!")
            return entities_at_position[0]
        return None
    
    def check_for_item_collision(self, player_position):
        items_at_position = self.items.get(player_position, [])
        if items_at_position:
            print(f"Player steps on {len(items_at_position)} items:")
            for item in items_at_position:
                print(f"  {item.name}!")
            return items_at_position[0]
        return None

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
                if (x, y) == player_position:
                    print(u.entities_data["player"]["symbol"], end=" ")
                else:
                    print(tile_symbol, end=" ")
            print()