import logic.entities as e
import logic.items as i
import logic.utils as u

class Map:
    def __init__(self, map_data, tiles_data, map_name):
        self.map_name = map_name
        self.map_data = map_data
        self.tiles_data = tiles_data
        self.map = self.create_map()
        self.entities = self.create_entities()
        self.items = self.create_items()

    def create_map(self):
        tile_map = []
        for row in self.map_data['tiles']:
            tile_map.append([self.tiles_data[tile]["symbol"] for tile in row])
        return tile_map

    def create_entities(self):
        entities = []
        for entity_data in self.map_data['entities']:
            entity_name = entity_data['name']
            entity_position = entity_data['position']
            entity_class = e.get_class_from_name(entity_name)

            if entity_name == "Player":
                entity = entity_class(u.entities_data["player"])
            else:
                entity = entity_class()

            entity.spawn_in_map(entity_position)
            entities.append(entity)
            print(f"Entity {entity_name} created at {entity_position}.")
        return entities

    def create_items(self):
        items = []
        for item_data in self.map_data['items']:
            item_name = item_data['name']
            item_position = item_data['position']
            item_class = i.get_class_from_name(item_name)
            item = item_class()
            item.spawn_in_map(item_position)
            items.append(item)
            print(f"Item {item_name} created at {item_position}.")
        return items


    def display(self):
        display_map = [row.copy() for row in self.map]

        for entity in self.entities:
            x, y = entity.position
            display_map[x][y] = entity.symbol

        for row in display_map:
            print(" ".join(row))

    def is_move_valid(self, new_position):
        x, y = new_position
        if 0 <= x < len(self.map) and 0 <= y < len(self.map[0]):
            tile_symbol = self.map[x][y]
            tile = next(t for t in self.tiles_data.values() if t["symbol"] == tile_symbol)
            return not tile["blocksMovement"]
        return False
