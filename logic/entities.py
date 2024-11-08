from logic.utils import items_data, loot_data
from logic.items import Weapon, Consumable
from logic.combat import CombatManager

## ENTITIES ##
class Entity:
    def __init__(self, data, position=(0, 0)):
        self.name = data["name"]
        self.description = data["description"]
        self.symbol = data["symbol"]
        self.health = data["health"]
        self.max_health = data["health"]
        self.attack = data["attack"]
        self.defense = data["defense"]
        self.experience = data["experience"]
        self.gold = data["gold"]
        self.inventory = data.get("inventory", [])
        self.position = position

    # Inventory
    def add_item(self, item_name):
        if isinstance(item_name, str):
            if item_name in items_data["weapons"]:
                return Weapon(items_data["weapons"][item_name])
            elif item_name in items_data["consumables"]:
                return Consumable(items_data["consumables"][item_name])
            else:
                print(f"Item {item_name} not found in the items data.")

    def print_inventory(self):
        print(f"{self.name}'s Inventory:")
        if not self.inventory:
            print("Your inventory is empty.")
        else:
            for index, item in enumerate(self.inventory, 1):
                print(f"{index}. {item.name} - {item.description if hasattr(item, 'description') else 'No description'}")


    def pick_up_item(self, item):
        from logic.gameloop import game_map
        self.inventory.append(item)
        print(f"{self.name} picked up {item.name}.")
        game_map.remove_loot(self.position, [item])

    def drop_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            from logic.gameloop import game_map
            game_map.drop_loot(self.position, [item])
            print(f"{self.name} dropped {item.name} on the ground.")
        else:
            print(f"{self.name} does not have {item.name} in their inventory.")

    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
        else:
            print(f"{self.name} does not have {item.name} in their inventory.")

    # Effects
    def effect(self, effect, amount):
        if effect == "health":
            self.health += amount
            print(f"{self.name} gained {amount} health.")
        elif effect == "defense":
            self.defense += amount
            print(f"{self.name} gained {amount} defense.")
        else:
            print(f"Effect {effect} not found.")

    # Combat
    def die(self):
        print(f"{self.name} has died!")


## PLAYER ##
class Player(Entity):
    def __init__(self, data):
        super().__init__(data)
        self.position = (1, 1)

    def move(self, direction, game_map):
        x, y = self.position
        if direction == "z":  # Haut
            new_position = (x, y - 1)
        elif direction == "s":  # Bas
            new_position = (x, y + 1)
        elif direction == "q":  # Gauche
            new_position = (x - 1, y)
        elif direction == "d":  # Droite
            new_position = (x + 1, y)
        else:
            new_position = self.position

        if self.is_position_valid(new_position, game_map):
            self.position = new_position
            self.check_for_enemy(new_position, game_map)
        elif self.is_position_enemy(new_position, game_map):
            print("You encounter an enemy!")
        elif self.position in game_map.loot_on_tiles:
            game_map.display_loot(self.position)
        else:
            print("Invalid move!")

    def is_position_valid(self, position, game_map):
        x, y = position
        return 0 <= x < len(game_map.current_map_tileset[0]) and 0 <= y < len(game_map.current_map_tileset)

    def is_position_enemy(self, position, game_map):
        for entity in game_map.inventory:
            if entity.position == position:
                return True
        return False

    def check_for_enemy(self, position, game_map):
        for enemy in game_map.entities:
            if enemy.position == position:
                print(f"You encounter {enemy.name}!")
                combat_manager = CombatManager(self, enemy)
                combat_manager.start_combat()
                break

    # Inventory
    def use_inventory(self):
        if not self.inventory:
            print("Your inventory is empty.")
            return

        print(f"Inventory: {self.name}")
        for i, item in enumerate(self.inventory):
            print(f"{i + 1}. {item.name} - {item.description}")

        choice = input("Choose an item to use (number): ")

        if choice.isdigit():
            choice = int(choice) - 1
            if 0 <= choice < len(self.inventory):
                item = self.inventory[choice]
                if isinstance(item, Consumable):
                    item.use(self)
                    self.inventory.remove(item)
                else:
                    print("You can't use this item.")
            else:
                print("Invalid choice.")
        else:
            print("Invalid input.")

## ENEMIES ##
class Enemy(Entity):
    def __init__(self, data, position):
        super().__init__(data, position)
        self.loot = data.get("loot", [])
        self.position = position

    def setup_loot_in_inventory(self):
        for item in loot_data[self.loot]["items"]:
            item_name = item["name"]
            item_quantity = item["quantity"]
            for _ in range(item_quantity):
                self.inventory.append(self.add_item(item_name))
                print(f"Adding {item_name} to {self.name}'s inventory.")

    def use_inventory(self):
        if not self.inventory:
            print(f"{self.name}'s inventory is empty.")
            return

        print(f"Inventory: {self.name}")
        for i, item in enumerate(self.inventory):
            print(f"{i + 1}. {item.name} - {item.description}")

        choice = input("Choose an item to use (number): ")

        if choice.isdigit():
            choice = int(choice) - 1
            if 0 <= choice < len(self.inventory):
                item = self.inventory[choice]
                if isinstance(item, Consumable):
                    item.use(self)
                    self.inventory.remove(item)
                else:
                    print("You can't use this item.")
            else:
                print("Invalid choice.")
        else:
            print("Invalid input.")

    # Combat
    def die(self):
        super().die()
        from logic.gameloop import game_map
        game_map.drop_loot(self.position, self.inventory)
        print(f"{self.name} dropped their loot on the ground!")