import json
import os

# Chargement des données JSON
def load_data():
    try:
        with open("data/entities.json", "r") as file:
            entities_data = json.load(file)
        
        with open("data/map.json", "r") as file:
            map_data = json.load(file)
        
        with open("data/items.json", "r") as file:
            items_data = json.load(file)
        
        return entities_data, map_data, items_data
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit()

entities_data, map_data, items_data = load_data()

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
    player.add_item(Sword())  # Ajouter une épée au joueur

    global game_map
    game_map = Map(map_data)

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
        self.entities = []  # Liste pour stocker les entités ennemies
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
                self.entities.append(new_entity)
                print(f"{new_entity.name} has been added to the map at position {entity_position}.")

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
        self.position = position
        self.inventory = []

    def add_item(self, item, quantity=1):
        for _ in range(quantity):
            self.inventory.append(item)

    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
        else:
            print(f"{self.name} does not have {item.name} in their inventory.")

    def use_item(self, item, in_combat=False):
        if isinstance(item, Weapon):
            if in_combat:
                print(f"{self.name} attacks with {item.name} in combat and deals {item.damage} damage.")
            else:
                print(f"{self.name} uses {item.name}... in the wind.")
        elif isinstance(item, Item):
            if in_combat:
                print(f"{self.name} uses {item.name} in combat.")
            else:
                print(f"{self.name} uses {item.name} outside of combat.")

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

    def use_item(self, item, in_combat=False):
        super().use_item(item, in_combat)

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
                break

    def print_inventory(self):
        if not self.inventory:
            print("Your inventory is empty!")
        else:
            print("Inventory:")
            for index, item in enumerate(self.inventory, 1):
                print(f"{index}. {item.name} - {item.description}")

## ENEMIES ##
class Enemy(Entity):
    def __init__(self, data, position):
        super().__init__(data, position)
        self.inventory = []

    def add_inventory(self):
        for item in self.inventory:
            for _ in range(item["quantity"]):
                self.add_item(Weapon(items_data["weapons"][item["type"]]))
                print(f"{self.name} loots {item['type']}")

## ITEMS ##
class Item:
    def __init__(self, data):
        self.name = data["name"]
        self.description = data["description"]

    def use(self, entity, in_combat=False):
        entity.use_item(self, in_combat)

    def apply_effect(self, entity):
        pass

class Weapon(Item):
    def __init__(self, data):
        super().__init__(data)
        self.damage = data["damage"]

    def use(self, entity, in_combat=False):
        entity.use_item(self, in_combat)

    def apply_effect(self, entity):
        entity.attack += self.damage

class Sword(Weapon):
    def __init__(self):
        sword_data = items_data["weapons"]["sword"]
        super().__init__(sword_data)

class Consumable(Item):
    def __init__(self, data):
        super().__init__(data)
        self.health = data["health"]

    def use(self, entity, in_combat=False):
        entity.use_item(self, in_combat)

    def apply_effect(self, entity):
        entity.health += self.health

## UTILS ##
def exit_game():
    print("Exiting game...")
    input("Press any key to continue...")
    quit()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()
