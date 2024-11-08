from logic.entities import Enemy
from logic.items import Weapon, Consumable
from logic.utils import items_data, entities_data

## MAP ##
class Map:
    def __init__(self, map_data):
        self.tiles = map_data["tiles"]
        self.map_layout = map_data["layout"]
        self.current_map_name = list(self.map_layout.keys())[0]
        self.current_map_description = self.map_layout[self.current_map_name]["description"]
        self.current_map_tileset = self.map_layout[self.current_map_name]["tileset"]
        self.current_map_inventory = self.map_layout[self.current_map_name]["inventory"]
        self.inventory = []
        self.entities = []
        self.loot_on_tiles = {}

        self.init_entities()
        self.init_items()

    def init_entities(self):
        inventory_entities = self.current_map_inventory.get("entities", [])
        if not inventory_entities:
            print("No entities found in the inventory.")
        for entity in inventory_entities:
            for _ in range(entity["quantity"]):
                entity_name = entity["name"]
                entity_position = tuple(entity["position"])
                new_entity = Enemy(entities_data[entity_name], entity_position)
                new_entity.setup_loot_in_inventory()
                self.entities.append(new_entity)
                print(f"Entity {entity_name} added to the map.")

    def init_items(self):
        inventory_items = self.current_map_inventory.get("items", [])
        if not inventory_items:
            print("No items found in the inventory.")
        for item in inventory_items:
            for _ in range(item["quantity"]):
                item_name = item["name"]
                item_position = tuple(item["position"])

                if item_name in items_data["weapons"]:
                    new_item = Weapon(items_data["weapons"][item_name], item_position)
                elif item_name in items_data["consumables"]:
                    new_item = Consumable(items_data["consumables"][item_name])
                else:
                    print(f"Item {item_name} not found in the items data.")
                    continue

                self.inventory.append(new_item)
                if item_position not in self.loot_on_tiles:
                    self.loot_on_tiles[item_position] = []
                self.loot_on_tiles[item_position].append(new_item)
                print(f"Item {item_name} added to the map at position {item_position}.")


    def print_map(self):
        from logic.gameloop import player
        print(f"Map: {self.current_map_name}")
        print(f"Description: {self.current_map_description}")
        for y, row in enumerate(self.current_map_tileset):
            for x, tile in enumerate(row):
                if (x, y) == player.position:
                    print(player.symbol, end=" ")
                elif (x, y) in self.loot_on_tiles:
                    print("L", end=" ")
                elif any(entity.position == (x, y) for entity in self.entities):
                    print(self.entities[0].symbol, end=" ")
                else:
                    print(tile, end=" ")
            print()

    def drop_loot(self, position, loot_items):
        if position in self.loot_on_tiles:
            self.loot_on_tiles[position].extend(loot_items)
        else:
            self.loot_on_tiles[position] = loot_items

    def display_loot(self, position):
        if position in self.loot_on_tiles:
            loot_list = self.loot_on_tiles[position]
            loot_count = {}

            for item in loot_list:
                if item.name in loot_count:
                    loot_count[item.name] += 1
                else:
                    loot_count[item.name] = 1

            print("Loot on the ground:")
            for item_name, quantity in loot_count.items():
                print(f"{item_name} x{quantity}")
            print("Type 'pick' to pick up loot.")
        else:
            print("No loot on the ground.")


    def pick_up_loot(self, position, item_index=None):
        from logic.gameloop import player
        loot_list = self.loot_on_tiles.get(position, [])
        if not loot_list:
            print("No loot to pick up.")
            return

        print("Loot available:")
        loot_count = {}
        for item in loot_list:
            if item.name in loot_count:
                loot_count[item.name] += 1
            else:
                loot_count[item.name] = 1

        for index, (item_name, quantity) in enumerate(loot_count.items(), 1):
            print(f"{index}. {item_name} x{quantity}")

        print("Choose items to pick up by numbers (e.g., '1,2').")
        print("Type 'all' to pick up all items.")
        print("Type 'cancel' to cancel the action.")
        choice = input("> ").lower()

        if choice == "cancel":
            print("Action canceled.")
            return

        if choice == "all":
            for item in loot_list:
                player.pick_up_item(item)
            self.remove_loot(position, loot_list)
            print("All loot picked up.")
            return

        choices = choice.split(',')
        for single_choice in choices:
            if single_choice.strip().isdigit():
                item_index = int(single_choice.strip()) - 1
                if 0 <= item_index < len(loot_count):
                    item_name = list(loot_count.keys())[item_index]
                    item_quantity = loot_count[item_name]

                    if item_quantity > 1:
                        print(f"How many {item_name} would you like to pick up? (1-{item_quantity}) ")
                        quantity_choice = input("> ")
                        if quantity_choice.isdigit():
                            quantity = int(quantity_choice)
                            for _ in range(quantity):
                                item = next((item for item in loot_list if item.name == item_name),     None)
                                if item:
                                    player.pick_up_item(item)
                                    self.remove_loot(position, [item])
                                else:
                                    print("Item not found.")
                        else:
                            print("Invalid quantity.")
                    else:
                        item = next((item for item in loot_list if item.name == item_name), None)
                        if item:
                            player.pick_up_item(item)
                            self.remove_loot(position, [item])
                        else:
                            print("Item not found.")
                else:
                    print(f"Invalid choice: {single_choice}")


            
    def remove_loot(self, position, items_to_remove):
        if position in self.loot_on_tiles:
            for item in items_to_remove:
                if item in self.loot_on_tiles[position]:
                    self.loot_on_tiles[position].remove(item)
            if not self.loot_on_tiles[position]:
                del self.loot_on_tiles[position]