import json
import os
import random

# Chargement des données JSON
def load_data():
    try:
        with open("data/entities.json", "r") as file:
            entities_data = json.load(file)
        
        with open("data/map.json", "r") as file:
            map_data = json.load(file)
        
        with open("data/items.json", "r") as file:
            items_data = json.load(file)

        with open("data/loot.json", "r") as file:
            loot_data = json.load(file)
        
        return entities_data, map_data, items_data, loot_data
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit()

entities_data, map_data, items_data, loot_data = load_data()

## MAIN ##
def main():
    main_menu()

## MAIN MENU ##
def main_menu():
    print("[1] - New Game")
    print("[X] - Exit")

    option = input("Choose an option: ").lower()

    if option == "1":
        new_game()
    elif option == "x":
        exit_game()
    else:
        print("Invalid option!")
        main_menu()

## NEW GAME ##
def new_game():
    print("Starting a new game...")
    global player
    player = Player(entities_data["player"])
    global game_map
    game_map = Map(map_data)

    hand = Hand()
    sword = Sword()
    health_potion = HealthPotion()
    defense_potion = DefensePotion()

    player.pick_up_item(hand)
    player.pick_up_item(sword)
    player.pick_up_item(health_potion)
    player.pick_up_item(defense_potion)

    print("Press any key to continue...")
    input()
    game_loop()

## GAME LOOP ##
def game_loop():
    while True:
        game_map.print_map()
        game_map.display_loot(player.position)
        player_action()

def player_action():
    print("\n# Would you like to move? <z/q/s/d>")
    print("# Type 'bag' to check your inventory.")
    print("# Type 'exit' to return to the main menu.")

    choice = input("> ").lower()

    if choice in ["z", "q", "s", "d"]:
        clear_screen()
        player.move(choice, game_map)
    elif choice == "bag":
        clear_screen()
        player.use_inventory()
    elif choice == "pick":
        game_map.pick_up_loot(player.position)
    elif choice == "exit":
        main_menu()
    else:
        print("Invalid option!")


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


    def pick_up_loot(self, position, item_index=None, item_type=None):
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
        self.inventory.append(item)
        print(f"{self.name} picked up {item.name}.")
        game_map.remove_loot(self.position, [item])

    def drop_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
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
        game_map.drop_loot(self.position, self.inventory)
        print(f"{self.name} dropped their loot on the ground!")

## ITEMS ##
class Item:
    def __init__(self, data, position=(0, 0)):
        self.name = data["name"]
        self.description = data["description"]
        self.position = position

## WEAPONS ##
class Weapon(Item):
    def __init__(self, data, position=(0, 0)):
        super().__init__(data)
        self.damage = data["damage"]
        self.position = position

    def use(self, entity, target):
        if not isinstance(target, Entity):
            print("Invalid target!")
            return
        
        miss_chance = random.randint(1, 100) <= 10
        if miss_chance:
            print(f"{entity.name}'s attack missed!")
            return
        
        defense_factor = random.uniform(0.5, 1.0) * target.defense
        adjusted_damage = self.damage - defense_factor

        adjusted_damage = max(adjusted_damage, 1)

        target.health -= adjusted_damage
        print(f"{entity.name} attacked {target.name} with {self.name} for {adjusted_damage} damage.")

class Hand(Weapon):
    def __init__(self):
        hand_data = items_data["weapons"]["hand"]
        super().__init__(hand_data)

class Sword(Weapon):
    def __init__(self):
        sword_data = items_data["weapons"]["sword"]
        super().__init__(sword_data)

## CONSUMABLES ##
class Consumable(Item):
    def __init__(self, data):
        super().__init__(data)
        self.effect = data["effect"]
        self.amount = data["amount"]

    def use(self, entity):
        effect = self.effect
        entity.effect(effect, self.amount)

class HealthPotion(Consumable):
    def __init__(self):
        health_potion_data = items_data["consumables"]["health_potion"]
        super().__init__(health_potion_data)

class DefensePotion(Consumable):
    def __init__(self):
        defense_potion_data = items_data["consumables"]["defense_potion"]
        super().__init__(defense_potion_data)

## COMBAT ##
class CombatManager:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

    def start_combat(self):
        print(f"A battle has started between {self.player.name} and {self.enemy.name}!\n")
        while self.player.health > 0 and self.enemy.health > 0:
            self.player_turn()
            if self.enemy.health <= 0:
                print(f"{self.enemy.name} has been defeated!")
                self.enemy.die()
                break

            self.enemy_turn()
            if self.player.health <= 0:
                print(f"{self.player.name} has been defeated!")
                self.player.die()
                break

    def display_health(self):
        print(f"{self.player.name} - Health: {self.player.health}")
        print(f"{self.enemy.name} - Health: {self.enemy.health}\n")

    def player_turn(self):
        self.display_health()
        print("Choose an action:")
        print("[1] Attack")
        print("[2] Use a consumable")
        print("[3] Run away")
        choice = input("> ")
        if choice == "1":
            print("Choose your weapon:")
            weapons = [item for item in self.player.inventory if isinstance(item, Weapon)]
            for index, item in enumerate(weapons, 1):
                print(f"{index}. {item.name} - Damage: {item.damage}")  

            weapon_choice = input("Select weapon number: ") 

            if weapon_choice.isdigit():
                weapon_choice = int(weapon_choice) - 1
                if 0 <= weapon_choice < len(weapons):
                    weapon = weapons[weapon_choice]
                    weapon.use(self.player, self.enemy)
                else:
                    print("Invalid weapon choice! Please enter a valid number.")
                    self.player_turn()
            else:
                print("Please enter a valid number.")
                self.player_turn()
        elif choice == "2":
            print("Choose a consumable:")
            consumables = [item for item in self.player.inventory if isinstance(item, Consumable)]

            for index, item in enumerate(consumables, 1):
                print(f"{index}. {item.name} - {item.description}")

            consumable_choice = input("Select consumable number: ")
            if consumable_choice.isdigit():
                consumable_choice = int(consumable_choice) - 1
                if 0 <= consumable_choice < len(consumables):
                    consumable = consumables[consumable_choice]
                    consumable.use(self.player)
                    self.player.remove_item(consumable)
                else:
                    print("Invalid consumable choice! Please enter a valid number.")
                    self.player_turn()
            else:
                print("Please enter a valid number.")
                self.player_turn()
                
        elif choice == "3":
            run_chance = random.randint(1, 100) <= 70
            if run_chance:
                print("You run away from the battle!")
                directions = ["z", "q", "s", "d"]
                random_direction = random.choice(directions)
                self.player.move(random_direction, game_map)
                game_loop()
            else:
                print("You failed to run away!")
                self.enemy_turn()
        else:
            print("Invalid choice!")
            self.player_turn()

    def enemy_turn(self):
        self.display_health()
        consumables = [item for item in self.enemy.inventory if isinstance(item, Consumable)]
        if consumables:
            consumable = random.choice(consumables)
            consumable.use(self.enemy)
            self.enemy.remove_item(consumable)
        else:
            weapons = [item for item in self.enemy.inventory if isinstance(item, Weapon)]
            if weapons:
                weapon = random.choice(weapons)
                weapon.use(self.enemy, self.player)
            else:
                print(f"{self.enemy.name} has no weapons or consumables to use!")
                print(f"{self.enemy.name} skips their turn.")



## UTILS ##
def exit_game():
    print("Exiting game...")
    input("Press any key to continue...")
    quit()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()
