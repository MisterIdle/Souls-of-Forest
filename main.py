import os
import json

RESET = "\033[0m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RED = "\033[31m"

player = None
current_map = None
max_width = 40

def main():
    splash_screen()

####################
# Intro
####################

def splash_screen():
    clear_screen()
    print(load_ascii_art("splash"))
    input("Press Enter to continue...")
    main_menu()

###################
# Main menu
####################

def main_menu():
    clear_screen()
    print(load_ascii_art("title"))
    text_manager.print_line()

    print("[1] New game")
    print("[2] Continue")
    print("[3] Credits")

    print("[X] Exit")

    text_manager.print_line()

    choice = input("Enter choice: ")

    if choice == "1":
        new_game()
    elif choice == "2":
        load_game()
    elif choice == "3":
        credits()
    elif choice.lower() == "x":
        exit_game()
    else:
        print("Invalid choice. Please try again.")
        main_menu()

def new_game():
    global player, current_map
    current_map = Map(data_maps)
    player = Player(current_map)

    player.add_item(Knife())
    player.add_item(HealthPotion())

    print("New game created.")
    gameloop()

def load_game():
    print("Available save files:")
    main_menu()

def credits():
    clear_screen()
    print("Game created by: MisterIdle")
    print("Ascii art by:")
    print("- Tombstones by Hayley Jane Wakenshaw")
    print("- Tree by jg")
    input("Press Enter to continue...")
    main_menu()

def exit_game():
    print("Exiting game...")
    exit()

####################
# Game loop
####################

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def gameloop():
    is_running = True

    while is_running:
        clear_screen()
        player.display_stats()
        text_manager.print_line()

        print("# Would you like to: <save> <bag> <exit>")
        choice = input("> ")

        if choice in ["q", "d", "z", "s", "n", "e", "w"]: 
            player.move(choice)
        elif choice == "save":
            player.save()
            print("Game saved.")
        elif choice == "bag":
            clear_screen()
            player.display_inventory(detailed=True)
            item_choice = input("Enter the number of the item you want to use or press any other key to cancel: ")

            if item_choice.isdigit() and 1 <= int(item_choice) <= len(player.inventory):
                item = player.inventory[int(item_choice) - 1]
                item.use()
            else:
                print("Action cancelled.")
        elif choice == "exit":
            is_running = False
        else:
            print("Invalid command. Please try again.")

    main_menu()


####################
# Map
####################

with open("data/tiles.json") as f:
    data_maps = json.load(f)

class Map:
    def __init__(self, map_data):
        self.tiles = map_data["tiles"]
        self.map_layout = map_data["maps"]
        self.current_map_name = list(self.map_layout.keys())[0]
        self.current_map = self.map_layout[self.current_map_name]["tiles"]
        self.teleport_destinations = map_data["maps"][self.current_map_name]["teleport_destinations"]

    def show_map(self):
        player_x, player_y = player.get_pos()

        for y, row in enumerate(self.current_map):
            for x, tile in enumerate(row):
                if x == player_x and y == player_y:
                    print(YELLOW + "@" + RESET, end=" ")
                else:
                    print(tile, end=" ")
            print()

    def get_name(self):
        return self.current_map_name
    
    def get_description(self):
        player_x, player_y = player.get_pos()
        tite_type = self.current_map[player_y][player_x]
        if tite_type in self.tiles:
            return self.tiles[tite_type]["description"]
        else:
            return "No description available."
        
    def teleport(self):
        print("Available destinations:")
        destination_names = list(self.teleport_destinations.keys())

        if len(destination_names) == 1:
            destination_name = destination_names[0]
            choice = input("Do you want to teleport to " + destination_name.upper() + "? (y/n): ")

            if choice.lower() == "y":
                self.current_map_name = destination_name
                self.current_map = self.map_layout[destination_name]["tiles"]
                self.teleport_destinations = self.map_layout[destination_name]  ["teleport_destinations"]

                print("Teleported to", destination_name)
            else:
                print("Teleportation cancelled.")
        else:
            for index, destination_name in enumerate(destination_names, start=1):
                print(f"{index}. {destination_name}")
            choice = input("Choose a destination or press any other key to cancel: ")

            if choice.isdigit() and 1 <= int(choice) <= len(destination_names):
                destination_name = destination_names[int(choice) - 1]
                self.current_map_name = destination_name
                self.current_map = self.map_layout[destination_name]["tiles"]
                self.teleport_destinations = self.map_layout[destination_name]["teleport_destinations"]

                print("Teleported to", destination_name)
            else:
                print("Teleportation cancelled.")
    
    def get_map_state(self):
        return self.current_map

    def load_map_state(self, state):
        self.current_map = state

####################
# Entity
####################

class Entity:
    def __init__(self, name, health, attack, defense, speed, exp=0, gold=0):
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.exp = exp
        self.gold = gold
        self.x = 1
        self.y = 1

    def get_pos(self):
        return self.x, self.y
    
####################
# Player
####################

class Player(Entity):
    def __init__(self, map_instance):
        super().__init__("Player", 100, 10, 5, 10)
        self.inventory = []
        self.map_instance = map_instance

    def display_stats(self):
        print("Name:", self.name)
        print("HP:", (GREEN), self.health, (RESET), " ATK:", self.attack, " DEF:", self.defense, " GOLD:", (YELLOW), self.gold, (RESET), "\n")

    def display_inventory(self, detailed=False):
        print("Inventory:")
        for index, item in enumerate(self.inventory, start=1):
            print(f"{index}. {item.name} x{item.quantity}")

            if detailed:
                print(item.description)
                print()

    def move(self, direction):
        x, y = self.get_pos()

        if direction == "z":  # Up
            y -= 1
        elif direction == "s":  # Down
            y += 1
        elif direction == "q":  # Left
            x -= 1
        elif direction == "d":  # Right
            x += 1

        if 0 <= y < len(self.map_instance.current_map) and 0 <= x < len(self.map_instance.current_map[0]):
            if self.map_instance.current_map[y][x] == "T":
                self.map_instance.teleport()
            else:
                self.x = x
                self.y = y
        else:
            print("Invalid move. Please try again.")

    def add_item(self, item):
        for inventory_item in self.inventory:
            if inventory_item.name == item.name:
                inventory_item.quantity += 1
                return

        self.inventory.append(item)

    def remove_item(self, item):
        self.inventory.remove(item)

####################
# Items
####################

with open("data/items.json", encoding='utf-8') as f:
    items_data = json.load(f)

class Item:
    def __init__(self, name, description, quantity=1):
        self.name = name
        self.description = description
        self.quantity = quantity

    def use(self):
        print(f"{self.name} used.")
        
        if not isinstance(self, (Weapon)):
            self.activate_effect()
            if self.quantity > 1:
                self.quantity -= 1
            else:
                player.remove_item(self) 

        else:
            print("Cannot use this item in this way.")

    def activate_effect(self):
        print("This item has no special effect.")

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

####################
# Weapons
####################

class Weapon(Item):
    def __init__(self, name, description, damage, critical=0):
        super().__init__(name, description)
        self.damage = damage
        self.critical = critical 

    def get_critical(self):
        return self.critical 

class Knife(Weapon):
    def __init__(self):
        data = items_data["items"]["weapon"]["knife"]
        super().__init__(data["name"], data["description"], data["damage"], data["critical"])

class Sword(Weapon):
    def __init__(self):
        data = items_data["items"]["weapon"]["sword"]
        super().__init__(data["name"], data["description"], data["damage"], data["critical"])

class Axe(Weapon):
    def __init__(self):
        data = items_data["items"]["weapon"]["axe"]
        super().__init__(data["name"], data.get("description", "An axe"), data["damage"], data["critical"])

####################
# Potions
####################

class Potion(Item):
    def __init__(self, name, description):
        super().__init__(name, description)


class HealthPotion(Potion):
    def __init__(self):
        data = items_data["items"]["potion"]["health"]
        super().__init__(data["name"], data["description"])

    def activate_effect(self):
        heal_amount = items_data["items"]["potion"]["health"]["heal"]
        player.health += heal_amount
        print(f"{self.name} used! You healed {heal_amount} health points.")

####################
# Text Manager
####################

class TextManager:
    def __init__(self):
        self.texts = {}

    def load_texts(self, filename):
        with open(filename, encoding='utf-8') as f:
            self.texts = json.load(f)

    def print_line(self):
        print("+" + "-" * max_width + "+")

text_manager = TextManager()

####################
# Utility functions
####################

def load_ascii_art(filename):
    with open(f"images/{filename}.txt", encoding="utf-8") as f:
        return f.read()
    
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()
