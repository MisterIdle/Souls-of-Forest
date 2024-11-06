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
    player.add_item(Knife())
    player.add_item(Sword())
    player.add_item(Axe())
    player.add_item(HealthPotion())
    player.add_item(HealthPotion())
    player.add_item(HealthPotion())
    player.add_item(DefensePotion())

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
    print("- Tree by ejm96")
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
        current_map.display_map()
        player.display_stats()
        current_map.show_compass()
        text_manager.print_line()

        print("\n # Would you like to: <save> <bag> <exit>")
        choice = input("> ")

        if choice in ["q", "d", "z", "s", "n", "e", "w"]: 
            player.move(choice)
        elif choice == "save":
            player.save()
            print("Game saved.")
        elif choice == "bag":
            clear_screen()
            player.display_inventory()
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
    
    def get_tite_name(self):
        player_x, player_y = player.get_pos()
        tite_type = self.current_map[player_y][player_x]
        if tite_type in self.tiles:
            return self.tiles[tite_type]["name"]
        else:
            return "No name available."
    
    def get_tite_description(self):
        player_x, player_y = player.get_pos()
        tite_type = self.current_map[player_y][player_x]
        if tite_type in self.tiles:
            return self.tiles[tite_type]["description"]
        else:
            return "No description available."
        
    def display_map(self):
        print("MAP: [" + self.current_map_name + "]")
        print("# " + self.get_tite_name())
        print("# " + self.get_tite_description())
        print()
        try:
            print(load_ascii_art(self.get_tite_name().lower()))
        except FileNotFoundError:
            print("No image available.")
        print()

    def show_compass(self):
        directions = {
            "NORTH": (0, -1),
            "WEST": (-1, 0),
            "EAST": (1, 0),
            "SOUTH": (0, 1)
        }
    
        player_x, player_y = player.get_pos()
    
        compass = {"NORTH": "Out of bounds", "WEST": "Out of bounds", "EAST": "Out of bounds", "SOUTH": "Out of bounds"}
    
        for direction, (dx, dy) in directions.items():
            adjacent_x = player_x + dx
            adjacent_y = player_y + dy
    
            if 0 <= adjacent_y < len(self.current_map) and 0 <= adjacent_x < len(self.current_map[0]):
                tile_type = self.current_map[adjacent_y][adjacent_x]
                compass[direction] = self.tiles[tile_type]["name"]
    
        # Afficher la boussole formatée
        text_manager.print_center("Compass")
        text_manager.print_line()
        text_manager.print_center(f"NORTH (N/Z)")
        text_manager.print_center(f"{compass['NORTH']}")
        text_manager.print_both(f"WEST (Q)", f"EAST (D)")
        text_manager.print_both(f"{compass['WEST']}", f"{compass['EAST']}")
        text_manager.print_center(f"SOUTH (S)")
        text_manager.print_center(f"{compass['SOUTH']}")


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
        text_manager.print_center("Player Stats")
        text_manager.print_left("Name: " + self.name)
        text_manager.print_left("HP: " + str(self.health) +  " ATK: " + str(self.attack) +" DEF: " + str(self.defense))
        print()

    def display_inventory(self):
        self.display_stats()
        text_manager.print_center("Inventory")
        text_manager.print_line()

        # Print only weapons
        for index, item in enumerate(self.inventory, start=1):
            if isinstance(item, Weapon):
                text_manager.print_left(f"{index}. {item.name} ({item.quantity})")
                text_manager.print_left(f"# {item.description}")
                text_manager.print_right(f"Damage: {item.damage} | Critical: {item.critical}% | {item.kilograms}kg")
                print()

        # Print only potions
        for index, item in enumerate(self.inventory, start=1):
            if isinstance(item, Potion):
                text_manager.print_left(f"{index}. {item.name} ({item.quantity})")
                text_manager.print_left(f"# {item.description}")
                text_manager.print_right(f"{item.kilograms}kg")
                print()
                
        print("\n # Choose an item to use or press any other key to close the inventory.")
        item_choice = input("> ")

        if item_choice.isdigit() and 1 <= int(item_choice) <= len(self.inventory):
            item = self.inventory[int(item_choice) - 1]
            item.use()
        else:
            print("Inventory closed.")

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
    def __init__(self, name, description, quantity=1, kilograms=0):
        self.name = name
        self.description = description
        self.quantity = quantity
        self.kilograms = kilograms

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
    def __init__(self, name, description, damage, critical=0, kilograms=0):
        super().__init__(name, description)
        self.damage = damage
        self.critical = critical
        self.kilograms = kilograms

    def get_critical(self):
        return self.critical 

class Knife(Weapon):
    def __init__(self):
        data = items_data["items"]["weapon"]["knife"]
        super().__init__(data["name"], data["description"], data["damage"], data["critical"], data["kilograms"])

class Sword(Weapon):
    def __init__(self):
        data = items_data["items"]["weapon"]["sword"]
        super().__init__(data["name"], data["description"], data["damage"], data["critical"], data["kilograms"])

class Axe(Weapon):
    def __init__(self):
        data = items_data["items"]["weapon"]["axe"]
        super().__init__(data["name"], data["description"], data["damage"], data["critical"], data["kilograms"])

####################
# Potions
####################

class Potion(Item):
    def __init__(self, name, description, kilograms=0):
        super().__init__(name, description)
        self.kilograms = kilograms


class HealthPotion(Potion):
    def __init__(self):
        data = items_data["items"]["potion"]["health"]
        super().__init__(data["name"], data["description"], data["kilograms"])

    def activate_effect(self):
        heal_amount = items_data["items"]["potion"]["health"]["heal"]
        player.health += heal_amount
        print(f"{self.name} used! You healed {heal_amount} health points.")

class DefensePotion(Potion):
    def __init__(self):
        data = items_data["items"]["potion"]["defense"]
        super().__init__(data["name"], data["description"], data["kilograms"])

    def activate_effect(self):
        defense_boost = items_data["items"]["potion"]["defense"]["boost"]
        player.defense += defense_boost
        print(f"{self.name} used! Your defense increased by {defense_boost} points.")

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

    def print_center(self, text):
        print(text.center(max_width))

    def print_left(self, text):
        print(text.ljust(max_width))

    def print_right(self, text):
        print(text.rjust(max_width))

    def print_both(self, left_text, right_text):
        print(left_text.ljust(max_width // 2) + right_text.rjust(max_width // 2))

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
