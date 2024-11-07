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
    player.inventory.append(hand)
    player.inventory.append(sword)
    player.inventory.append(health_potion)

    print("Press any key to continue...")
    input()
    game_loop()

## GAME LOOP ##
def game_loop():
    while True:
        game_map.print_map()
        player_action()

def player_action():
    print("\n# Would you like to move? <z/q/s/d>, open your bag <bag> or exit <exit>")
    choice = input("> ").lower()

    if choice in ["z", "q", "s", "d"]:
        clear_screen()
        player.move(choice, game_map)
    elif choice == "bag":
        player.print_inventory()

        print("Which item would you like to use? (Enter number or 'cancel' to go back)")
        item_choice = input("> ").lower()

        if item_choice == "cancel":
            print("Action canceled.")
        else:
            try:
                item_index = int(item_choice) - 1
                if 0 <= item_index < len(player.inventory):
                    item = player.inventory[item_index]
                    if isinstance(item, Weapon):
                        target = None
                        for enemy in game_map.entities:
                            if enemy.position == player.position:
                                target = enemy
                                break
                        if target:
                            item.use(player, target)
                        else:
                            print("No enemy in range to attack!")
                    else:
                        item.use(player)
                else:
                    print("Invalid item number!")
            except ValueError:
                print("Invalid input! Please enter a valid number or 'cancel'.")
            
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
        self.init_entities()

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


    def print_map(self):
        print(f"Map: {self.current_map_name}")
        print(f"Description: {self.current_map_description}")
        
        for y, row in enumerate(self.current_map_tileset):
            for x, tile in enumerate(row):
                if (x, y) == player.position:
                    print(player.symbol, end=" ")
                else:
                    enemy_here = False
                    for enemy in self.entities:
                        if enemy.position == (x, y):
                            print(enemy.symbol, end=" ")
                            enemy_here = True
                    if not enemy_here:
                        print(tile, end=" ")
            print()

## ENTITIES ##
class Entity:
    def __init__(self, data, position=(0, 0)):
        self.name = data["name"]
        self.description = data["description"]
        self.symbol = data["symbol"]
        self.health = data["health"]
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
        if not self.inventory:
            print("Your inventory is empty!")
        else:
            print("Inventory:")
            for index, item in enumerate(self.inventory, 1):
                print(f"{index}. {item.name} - {item.description}")

    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
        else:
            print(f"{self.name} does not have {item.name} in their inventory.")

    # Combat
    def die(self):
        print(f"{self.name} has died!")

    def use_item(self, item):
        print(f"{self.name} uses {item.name}.")


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

    # Combat
    def use_item(self, item, target=None):
        if isinstance(item, Weapon):
            if target:
                item.use(self, target)
            else:
                print("No target to attack.")
        elif isinstance(item, Consumable):
            item.use(self)
        else:
            print(f"{item.name} cannot be used.")

## ENEMIES ##
class Enemy(Entity):
    def __init__(self, data, position):
        super().__init__(data, position)
        self.loot = data.get("loot", [])

    def setup_loot_in_inventory(self):
        for item in loot_data[self.loot]["items"]:
            item_name = item["name"]
            item_quantity = item["quantity"]
            for _ in range(item_quantity):
                self.inventory.append(self.add_item(item_name))
                print(f"Adding {item_name} to {self.name}'s inventory.")

    # Combat
    def die(self):
        super().die()
        print(f"{self.name} drops:")
        for item in self.inventory:
            print(f"{item.name} - {item.description}")

    def use_item(self, item):
        item.use(self)

## ITEMS ##
class Item:
    def __init__(self, data):
        self.name = data["name"]
        self.description = data["description"]

    def apply_effect(self, entity):
        pass

class Weapon(Item):
    def __init__(self, data):
        super().__init__(data)
        self.damage = data["damage"]

    def use(self, entity, target):
        self.apply_effect(entity, target)

    def apply_effect(self, entity, target):
        miss_chance = random.randint(1, 100) <= 10
        if miss_chance:
            print(f"{entity.name}'s attack missed!")
            return
        
        defense_factor = random.uniform(0.5, 1.0) * target.defense
        adjusted_damage = self.damage - defense_factor

        adjusted_damage = max(adjusted_damage, 1)

        target.health -= adjusted_damage

class Hand(Weapon):
    def __init__(self):
        hand_data = items_data["weapons"]["hand"]
        super().__init__(hand_data)

class Sword(Weapon):
    def __init__(self):
        sword_data = items_data["weapons"]["sword"]
        super().__init__(sword_data)

class Consumable(Item):
    def __init__(self, data):
        super().__init__(data)
        self.health = data["health"]

    def use(self, entity):
        self.apply_effect(entity)
        entity.remove_item(self)

class HealthPotion(Consumable):
    def __init__(self):
        health_potion_data = items_data["consumables"]["health_potion"]
        super().__init__(health_potion_data)

    def apply_effect(self, entity):
        entity.health += self.health

## COMBAT ##
class CombatManager:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

    def start_combat(self):
        print(f"Combat started between {self.player.name} and {self.enemy.name}!")

        while self.player.health > 0 and self.enemy.health > 0:
            self.print_status()
            self.player_turn()
            if self.enemy.health <= 0:
                print(f"{self.enemy.name} has been defeated!")
                break
            self.enemy_turn()
            if self.player.health <= 0:
                print(f"{self.player.name} has been defeated!")
                break

    def print_status(self):
        print(f"{self.player.name} - Health: {round(self.player.health, 2)} - Attack: {self.player.attack} - Defense: {self.player.defense}")
        print(f"{self.enemy.name} - Health: {round(self.enemy.health, 2)} - Attack: {self.enemy.attack} - Defense: {self.enemy.defense}")

    def player_turn(self):
        print("\nChoose an action: [1] - Attack, [2] - Use item, [3] - Run")
        choice = input("> ")

        if choice == "1":
            self.player_attack()
        elif choice == "2":
            self.player_use_item()
        elif choice == "3":
            self.run_away()
        else:
            print("Invalid choice, try again!")
            self.player_turn()

    def player_attack(self):
        weapons = [item for item in self.player.inventory if isinstance(item, Weapon)]

        if weapons:
            for index, weapon in enumerate(weapons, 1):
                print(f"{index}. {weapon.name} - {weapon.description}")

            print("Which weapon would you like to use? (Enter number)")
            weapon_choice = input("> ")
            try:
                weapon_index = int(weapon_choice) - 1
                if 0 <= weapon_index < len(weapons):
                    weapon = weapons[weapon_index]
                    weapon.use(self.player, self.enemy)
                else:
                    print("Invalid weapon number!")
            except ValueError:
                print("Invalid input! Please enter a valid number.")
        else:
            print("You have no weapons in your inventory!")

    def player_use_item(self):
        consumables = [item for item in self.player.inventory if isinstance(item, Consumable)]
        if consumables:
            for index, consumable in enumerate(consumables, 1):
                print(f"{index}. {consumable.name} - {consumable.description}")

            print("Which item would you like to use? (Enter number)")
            item_choice = input("> ")
            try:
                item_index = int(item_choice) - 1
                if 0 <= item_index < len(consumables):
                    item = consumables[item_index]
                    item.use(self.player)
                else:
                    print("Invalid item number!")
            except ValueError:
                print("Invalid input! Please enter a valid number.")
        else:
            print("You have no consumables in your inventory!")

    def run_away(self):
        print(f"{self.player.name} attempts to run away!")
        success_chance = random.randint(1, 100)
        if success_chance > 50:
            print(f"{self.player.name} successfully ran away!")
            return
        else:
            print(f"{self.player.name} failed to escape!")

    def enemy_turn(self):
        print(f"{self.enemy.name} attacks!")

        if self.enemy.health < 30:
            consumables = [item for item in self.enemy.inventory if isinstance(item, Consumable)]

            if not consumables:
                print(f"{self.enemy.name} has no consumables to use!")
                weapons = [item for item in self.enemy.inventory if isinstance(item, Weapon)]
                if weapons:
                    weapon = weapons[0]
                    weapon.use(self.enemy, self.player)
                    print(f"{self.enemy.name} used {weapon.name}!")
                return

            if consumables:
                consumable = consumables[0]
                consumable.use(self.enemy)
                print(f"{self.enemy.name} used {consumable.name}!")
                return
        
        # Enemy attacks with its weapon
        weapons = [item for item in self.enemy.inventory if isinstance(item, Weapon)]
        if weapons:
            weapon = weapons[0]  # Assuming the enemy uses the first weapon in the list
            weapon.use(self.enemy, self.player)
        else:
            print(f"{self.enemy.name} has no weapon to attack with!")



## UTILS ##
def exit_game():
    print("Exiting game...")
    input("Press any key to continue...")
    quit()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()
