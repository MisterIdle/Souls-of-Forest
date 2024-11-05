import os
import random

def main():
    main_menu()

###################
# Main menu
####################

def main_menu():
    clear_screen()
    print("=== Main Menu ===")
    print("1. New Game")
    print("2. Load Game")
    print("3. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        new_game()
    elif choice == "2":
        load_game()
    elif choice == "3":
        exit_game()
    else:
        print("Invalid choice. Please try again.")
        main_menu()

def new_game():
    global player, current_map

    player_name = input("Enter your name: ")
    player = Player(player_name)

    player.add_to_inventory(Sword())
    player.add_to_inventory(HealthPotion())
    player.current_map_name = "forest"

    current_map = Map(data_maps[player.current_map_name])

    print(f"Welcome, {player_name}!")
    input("Press Enter to continue...")

    gameloop()

def load_game():
    print("Loading game...")
    print("No save files found.")
    main_menu()

def exit_game():
    print("Exiting game...")
    exit()

####################
# GAME LOOP
####################

def gameloop():
    clear_screen()

    # Stats
    player.show_stats()

    # Inventory
    player.show_inventory()

    # Location
    current_location = get_location(player.x, player.y)
    current_location.show_info()

    # Debug show map
    current_map.show(player.x, player.y)

    # Surroundings
    show_surroundings(player.x, player.y)

    # Error message
    show_error_message()

    # Actions
    print("# Would you like to: <look>? <use>? <quit>?")
    action = input("> ")

    if action == "look":
        current_location.show_info()
    elif action == "z" or action == "q" or action == "s" or action == "d" or action == "n" or action == "e" or action == "w":
        player.move(action)
    elif action == "use":
        clear_screen()
        player.show_inventory()
        item_number = int(input("Enter the item number to use: "))
        player.use_item(item_number)
    elif action == "quit":
        main_menu()
    else:
        change_message("Invalid action. Please try again.")

    gameloop()


####################
# Map
####################

data_maps = {
    "forest": [
        ["F", "F", "F", "F", "F"],
        ["F", "F", "F", "F", "F"],
        ["F", "F", "F", "F", "F"],
        ["F", "F", "F", "F", "F"],
        ["F", "F", "F", "F", "F"],
    ],

    "cave": [
        ["C", "C", "C", "C", "C"],
        ["C", "C", "C", "C", "C"],
        ["C", "C", "C", "C", "C"],
        ["C", "C", "C", "C", "C"],
        ["C", "C", "C", "C", "C"],
    ],
}

class Map:
    def __init__(self, data):
        self.data = data

    def show(self, player_x, player_y):
        map_copy = [row[:] for row in self.data]

        for y in range(len(map_copy)):
            for x in range(len(map_copy[0])):
                distance = abs(player_x - x) + abs(player_y - y)
                if distance > 5:
                    map_copy[y][x] = ' '

        if 0 <= player_y < len(map_copy) and 0 <= player_x < len(map_copy[0]):
            map_copy[player_y][player_x] = '@'

        for row in map_copy:
            print(" ".join(row))

class Location:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def show_info(self):
        name = f" {self.name} "
        border = "+" + "~" * (len(name) + 2) + "+"
        
        print()
        print((YELLOW) + border + (RESET))
        print(f"| {name} |")
        print((YELLOW) + border + (RESET))
        print("# " + self.description)
        print()


class Forest(Location):
    def __init__(self):
        super().__init__("Forest", "You are in a dense forest filled with trees.")

class Cave(Location):
    def __init__(self):
        super().__init__("Cave", "You are in a dark, damp cave.")

class Teleporter(Location):
    def __init__(self, current_map, x, y, destination_map, dest_x, dest_y):
        super().__init__("Teleporter", "A mystical portal.")
        self.current_map = current_map
        self.x = x
        self.y = y
        self.destination_map = destination_map
        self.dest_x = dest_x
        self.dest_y = dest_y

    def teleport(self, player):
        player.current_map_name = self.destination_map
        player.x = self.dest_x
        player.y = self.dest_y
        print(f"You have been teleported to {self.destination_map} at position ({self.dest_x}, {self.dest_y}).")

    @classmethod
    def place_teleport(cls, current_map, x, y, destination_map, dest_x, dest_y):
        if current_map in data_maps and \
           0 <= y < len(data_maps[current_map]) and \
           0 <= x < len(data_maps[current_map][y]):
            data_maps[current_map][y][x] = "T"
            teleporter = cls(current_map, x, y, destination_map, dest_x, dest_y)
            print(f"Teleporter placed at {current_map} ({x}, {y}) leading to {destination_map} ({dest_x}, {dest_y}).")
            return teleporter
        else:
            print("Invalid coordinates for placing the teleporter.")
            return None

def get_location(x, y):
    location = data_maps[player.current_map_name][y][x]
    if location == "F":
        return Forest()
    elif location == "C":
        return Cave()
    elif location == "T":
        return Teleporter("forest", 1, 1)
    else:
        return Location("Unknown", "You are in an unknown location.")

def show_surroundings(x, y):
    directions = {
        "NORTH": (x, y - 1),
        "SOUTH": (x, y + 1),
        "EAST": (x + 1, y),
        "WEST": (x - 1, y)
    }
    
    print("Surroundings:")
    for direction, (new_x, new_y) in directions.items():
        if 0 <= new_y < len(data_maps[player.current_map_name]) and 0 <= new_x < len(data_maps[player.current_map_name][0]):
            location = get_location(new_x, new_y)
            print(f"{direction}: {location.name}")


####################
# Battle
####################

####################
# Entity
####################

class Entity:
    def __init__(self, name):
        self.name = name
        self.hp = 100
        self.attack = 10
        self.defense = 5
        self.x = 1
        self.y = 1
        self.inventory = {}

    def show_stats(self):
        print((GREEN) + f"=== {self.name}'s stats ===" + (RESET))
        print(f"HP: {self.hp}")
        print(f"Attack: {self.attack}")
        print(f"Defense: {self.defense}")
        print()
        
    def getpos(self):
        return self.x, self.y

####################
# Player
####################

class Player(Entity):
    def __init__(self, name):
        super().__init__(name)
        self.inventory = {}
        self.current_map_name = "forest"

    def show_inventory(self):
        print("  [INVENTORY]  ")
        for i, item_name in enumerate(self.inventory):
            item = self.inventory[item_name]
            if not isinstance(item, Weapon):
                print(f"{i + 1}. {item} ({item.count})")
            else:
                print(f"{i + 1}. {item}")

    def add_to_inventory(self, item):
        if item.name in self.inventory:
            self.inventory[item.name].count += 1
        else:
            self.inventory[item.name] = item

    def remove_from_inventory(self, item_name):
        if item_name in self.inventory:
            self.inventory[item_name].count -= 1
            if self.inventory[item_name].count <= 0:
                del self.inventory[item_name]

    def use_item(self, item_number):
        try:
            item_name = list(self.inventory.keys())[item_number - 1]
            item_object = self.inventory[item_name]

            if isinstance(item_object, Weapon):
                print("You can't use a weapon.")
            elif isinstance(item_object, Potion):
                item_object.use(self)
                self.remove_from_inventory(item_name)
            elif isinstance(item_object, Sort):
                item_object.use(self)
                self.remove_from_inventory(item_name)
            else:
                print("You can't use that item.")
        except IndexError:
            print("Invalid item number. Please try again.")


    def move(self, direction):
        dx, dy = 0, 0

        if direction == "z" or direction == "n":
            dy = -1
        elif direction == "s":
            dy = 1
        elif direction == "q" or direction == "w":
            dx = -1
        elif direction == "d" or direction == "e":
            dx = 1

        new_x = self.x + dx
        new_y = self.y + dy

        if 0 <= new_y < len(data_maps[self.current_map_name]) and 0 <= new_x < len(data_maps[self.current_map_name][0]):
            location = get_location(new_x, new_y)
            if isinstance(location, Teleporter):
                location.teleport(self, current_map, new_x, new_y)
            elif location.name == "Unknown":
                change_message("You can't move there.")
            else:
                self.x = new_x
                self.y = new_y
        else:
            change_message("You can't move there.")

####################
# Enemy
####################

class Enemy(Entity):
    def __init__(self, name, attack):
        super().__init__(name)
        self.attack = attack

class Slime(Enemy):
    def __init__(self):
        super().__init__("Slime", attack=5)

class Goblin(Enemy):
    def __init__(self):
        super().__init__("Goblin", attack=10)

class Dragon(Enemy):
    def __init__(self):
        super().__init__("Dragon", attack=20)

####################
# Item
####################

class Item:
    def __init__(self, name):
        self.name = name
        self.count = 1

    def __str__(self):
        return self.name

####################
# Weapon
####################

class Weapon(Item):
    def __init__(self, name, attack_power):
        super().__init__(name)
        self.attack_power = attack_power

    def __str__(self):
        return f"{self.name} ({self.attack_power} AP)"

    def attack(self):
        return self.attack_power
    
class Sword(Weapon):
    def __init__(self):
        super().__init__("Sword", attack_power=10)

class Axe(Weapon):
    def __init__(self):
        super().__init__("Axe", attack_power=15)

class Bow(Weapon):
    def __init__(self):
        super().__init__("Bow", attack_power=20)

####################
# Potion
####################

class Potion(Item):
    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return self.name

class HealthPotion(Potion):
    def __init__(self):
        super().__init__("Health Potion")

    def use(self, entity):
        entity.hp += 20
        print(f"{entity.name} used {self.name} and gained 20 HP.")

class DefensePotion(Potion):
    def __init__(self):
        super().__init__("Defense Potion")

    def use(self, entity):
        entity.defense += 5
        print(f"{entity.name} used {self.name} and gained 5 defense.")

####################
# SORT
####################

class Sort(Item):
    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return self.name
    
class MapSort(Sort):
    def __init__(self):
        super().__init__("Map Sort")

    def use(self, entity):
        clear_screen()
        print("You used the Map Sort and revealed the map.")
        current_map.show(player.x, player.y)
        input("Press Enter to continue...")

####################
# Utility functions
####################

RESET = "\033[0m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RED = "\033[31m"

err_message = ""

def change_message(new_message):
    global err_message
    err_message = new_message

def show_error_message():
    global err_message
    if err_message:
        print()
        print((RED) + err_message + (RESET))
        print()
        err_message = ""

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()
