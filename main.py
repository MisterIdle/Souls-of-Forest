import os
import random
import json
import sys
import io

RESET = "\033[0m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RED = "\033[31m"

player = None
current_map = None

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

    # Si le dossier saves n'existe pas, on le crée
    if not os.path.exists("saves"):
        os.makedirs("saves")

    save_file = input("Enter a name for your game: ") + ".json"

    while os.path.exists(os.path.join("saves", save_file)) or save_file == ".json":
        if os.path.exists(os.path.join("saves", save_file)):
            print("Save file already exists. Please choose another name.")
        else:
            print("Invalid name. Please try again.")
        save_file = input("Enter a name for your game: ") + ".json"
    
    current_map = Map(data_maps)
    player = Player(current_map, save_file)
    player.add_item(Knife())
    print("New game created.")
    gameloop()

def load_game():
    global player, current_map
    save_files = os.listdir("saves")
    if not save_files:
        print("No save files found.")
        main_menu()
        input("Press Enter to continue...")
    
    print("Save files:")
    for index, save_file in enumerate(save_files, start=1):
        print(f"{index}. {save_file}")

    choice = input("Enter the number of the save file you want to load or press 'q' to go back: ")

    if choice.isdigit() and 1 <= int(choice) <= len(save_files):
        save_file = save_files[int(choice) - 1]
        current_map = Map(data_maps)
        player = Player(current_map, save_file)
        print("Game loaded.")
        gameloop()
    elif choice.lower() == "q":
        main_menu()
    else:
        clear_screen()
        print("Invalid choice. Please try again.")
        load_game()

def exit_game():
    print("Exiting game...")
    exit()

####################
# Game loop
####################

def gameloop():
    is_running = True

    while is_running:
        clear_screen()
        print("=== Game ===")
        
        print(current_map.get_description())
        
        current_map.show_map()

        # Show player inventory
        player.display_inventory()

        choice = input("Enter command: ")

        if choice in ["q", "d", "z", "s", "n", "e", "w"]: 
            player.move(choice)
        elif choice == "save":
            player.save()
            print("Game saved.")
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

    def get_description(self):
        player_x, player_y = player.get_pos()
        tile_type = self.current_map[player_y][player_x]
        if tile_type in self.tiles:
            return self.tiles[tile_type]["description"]
        else:
            return "Unknown location. (DEBUG ONLY!)"

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

class Player(Entity):
    def __init__(self, map_instance, save_file="save1.json"):
        self.save_file_path = os.path.join("saves", save_file)
        
        if not os.path.exists("saves"):
            os.makedirs("saves")

        if os.path.exists(self.save_file_path):
            with open(self.save_file_path, encoding='utf-8') as f:
                player_data = json.load(f)
        else:
            player_data = self.create_default_data()
        
        super().__init__(
            player_data["name"],
            player_data["health"],
            player_data["attack"],
            player_data["defense"],
            player_data["speed"],
            player_data["exp"],
            player_data["gold"]
        )
        self.inventory = [self.create_item(item) for item in player_data["inventory"]]
        self.x = player_data["position"]["x"]
        self.y = player_data["position"]["y"]
        self.map_instance = map_instance


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
                self.save()
        else:
            print("Invalid move. Please try again.")

    def add_item(self, item):
        self.inventory.append(item)

    def remove_item(self, item):
        self.inventory.remove(item)

    def display_inventory(self):
        print("Inventory:")
        for index, item in enumerate(self.inventory, start=1):
            print(f"{index}. {item.get_name()} - {item.get_description()}")

    # Save logic
    def save(self):
        player_data = {
            "name": self.name,
            "health": self.health,
            "attack": self.attack,
            "defense": self.defense,
            "speed": self.speed,
            "exp": self.exp,
            "gold": self.gold,
            "inventory": [item.get_name() for item in self.inventory],
            "position": {"x": self.x, "y": self.y}
        }
        save_manager.save_game(player_data, self.save_file_path)

    def create_default_data(self):
        return {
            "name": "Player",
            "health": 100,
            "attack": 10,
            "defense": 5,
            "speed": 5,
            "exp": 0,
            "gold": 0,
            "inventory": [],
            "position": {"x": 1, "y": 1}
        }

####################
# Save slots
####################

class SaveManager:
    def save_game(self, data, save_file):
        with open(save_file, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def load_game(self, save_file):
        with open(save_file, encoding='utf-8') as f:
            return json.load(f)

    def delete_save(self, save_file):
        os.remove(save_file)

    def get_save_files(self):
        return os.listdir("saves")

    def create_save_file(self, save_file):
        with open(save_file, "w") as f:
            pass

save_manager = SaveManager()

####################
# Items
####################

with open("data/items.json", encoding='utf-8') as f:
    items_data = json.load(f)

class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def use(self):
        print("Item used:", self.name)

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
# Utility functions
####################

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()
