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
    print("Starting new game...")
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
    player.show_stats()
    location = get_location(player.x, player.y)
    location.show_info()
    game_map.show()
    print("=======================")
    player.show_inventory()
    print("=======================")
    print("1: Use Item")
    print("Move: Z/Q/S/D or N/S/E/W")

    move = input("What is the next move: ")

    if move == "1":
        item_number = input("Enter the item number to use (or type 'cancel' to go back): ")
        if item_number.lower() == 'cancel':
            print("Cancelled item usage.")
        else:
            try:
                item_number = int(item_number)
                player.use_item(item_number)
            except ValueError:
                print("Invalid input. Please enter a number or 'cancel'.")
    else:
        old_x, old_y = player.x, player.y
        player.move(move.lower())

        # Check for enemy encounter
        if (player.x, player.y) != (old_x, old_y):  # Check if the player moved
            enemy_symbol = data_map[player.y][player.x]
            if enemy_symbol == "S":
                battle(player, Slime())
                data_map[player.y][player.x] = "."  # Remove enemy from the map
            elif enemy_symbol == "G":
                battle(player, Goblin())
                data_map[player.y][player.x] = "."  # Remove enemy from the map
            elif enemy_symbol == "D":
                battle(player, Dragon())
                data_map[player.y][player.x] = "."  # Remove enemy from the map
            else:
                print("No enemy here.")

    gameloop()

####################
# Map
####################

data_map = [
    ["#", "#", "#", "#", "#"],
    ["#", ".", ".", "S", "#"],
    ["#", "G", ".", ".", "#"],
    ["#", ".", "D", ".", "#"],
    ["#", "#", "#", "#", "#"],
]


class Map:
    def __init__(self, data):
        self.data = data

    def show(self):
        map_copy = [row[:] for row in self.data]
        
        px, py = player.getpos()
        
        if 0 <= py < len(map_copy) and 0 <= px < len(map_copy[0]):
            map_copy[py][px] = "@"

        for row in map_copy:
            print(" ".join(row))

game_map = Map(data_map)

class Location:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def show_info(self):
        print("=======================")
        print(f"Location: {self.name}")
        print("=======================")
        print(self.description)
        print("=======================")

class Forest(Location):
    def __init__(self):
        super().__init__("Forest", "Oh là là, cela fait peur ici!")

def get_location(x, y):
    if 0 <= y < len(data_map) and 0 <= x < len(data_map[0]):
        location_symbol = data_map[y][x]
        if location_symbol == "F":
            return Forest()
        else:
            return Location("Unknown", "This place is unknown.")
    return Location("Unknown", "This place is unknown.")

####################
# Battle
####################

def battle(player, enemy):
    print(f"A wild {enemy.name} appears!")
    while player.hp > 0 and enemy.hp > 0:
        print("=======================")
        print(f"{player.name}: {player.hp} HP")
        print(f"{enemy.name}: {enemy.hp} HP")
        print("=======================")

        # Tour du joueur
        player_turn(player, enemy)
        
        if enemy.hp > 0:  # Vérifie si l'ennemi est toujours en vie
            enemy_turn(player, enemy)  # Tour de l'ennemi, stats affichées après l'attaque

    # Déterminer l'issue de la bataille
    if player.hp <= 0:
        print(f"{player.name} has been defeated!")
    elif enemy.hp <= 0:
        print(f"{enemy.name} has been defeated!")
    print("Battle ended.")

def player_turn(player, enemy):
    print("\nYour turn!")
    print("1: Attack")
    print("2: Use Item")
    choice = input("What will you do? ")

    if choice == "1":
        print("Available Weapons:")
        weapons = [item for item in player.inventory.values() if isinstance(item, Weapon)]
        for i, weapon in enumerate(weapons):
            print(f"{i + 1}: {weapon.name}")

        weapon_choice = input("Enter the weapon number to use: ")
        try:
            weapon_choice = int(weapon_choice) - 1
            weapon = weapons[weapon_choice]
            damage = weapon.attack()
            enemy.hp -= damage
            print(f"You attack {enemy.name} for {damage} damage!")
            print(f"{enemy.name} has {enemy.hp} HP left!")
        except (ValueError, IndexError):
            print("Invalid weapon choice.")
            battle(player, enemy)

    elif choice == "2":
        print("Usable Items:")
        items = [item for item in player.inventory.values() if isinstance(item, Potion)]
        for i, item in enumerate(items):
            print(f"{i + 1}: {item.name}")

        item_choice = input("Enter the item number to use: ")
        try:
            item_choice = int(item_choice) - 1
            item = items[item_choice]
            item.use(player)
            print(f"{player.name} uses {item.name}. Current HP: {player.hp}")
        except (ValueError, IndexError):
            print("Invalid item choice.")
            battle(player, enemy)
    else:
        print("Invalid choice. Please try again.")
        battle(player, enemy)

def enemy_turn(player, enemy):
    damage = 5  # Exemple de dégâts infligés par l'ennemi
    player.hp -= damage
    print(f"{enemy.name}'s turn!")
    print(f"{enemy.name} attacks {player.name} for {damage} damage! {player.name} has {player.hp} HP left.")

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
        print("=======================")
        print(f"Name: {self.name}")
        print(f"HP: {self.hp}")
        print(f"Attack: {self.attack}")
        print(f"Defense: {self.defense}")
        print("=======================")

    def getpos(self):
        return self.x, self.y

####################
# Player
####################

class Player(Entity):
    def __init__(self, name):
        super().__init__(name)

    def show_inventory(self):
        print("Inventory:")
        for i, item in enumerate(self.inventory.values()):
            print(f"{i + 1}: {item}")

    def show_usable_items(self):
        print("Usable Items:")
        usable_items = [item for item in self.inventory.values() if isinstance(item, Potion)]
        for i, item in enumerate(usable_items):
            print(f"{i + 1}: {item.name}")

    def add_to_inventory(self, item):
        self.inventory[item.name] = item

    def remove_from_inventory(self, item_name):
        del self.inventory[item_name]

    def use_item(self, item_number):
        try:
            item = list(self.inventory.values())[item_number - 1]
            if isinstance(item, Potion):
                item.use(self)
                del self.inventory[item.name]
            else:
                print("You can't use that item.")
        except IndexError:
            print("Invalid item number. Please try again.")

    def move(self, direction):
        if (direction == "n" or direction == "z") and self.y > 0:
            self.y -= 1
        elif direction == "s" and self.y < len(data_map) - 1:
            self.y += 1
        elif (direction == "e" or direction == "d") and self.x < len(data_map[0]) - 1:
            self.x += 1
        elif (direction == "w" or direction == "q") and self.x > 0:
            self.x -= 1
        else:
            print("You can't move in that direction.")

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

class Weapon(Item):
    def __init__(self, name, attack_power):
        super().__init__(name)
        self.attack_power = attack_power

    def attack(self):
        return self.attack_power

class Potion(Item):
    def __init__(self, name, healing_amount):
        super().__init__(name)
        self.healing_amount = healing_amount

    def use(self, player):
        player.hp += self.healing_amount
        print(f"{player.name} heals for {self.healing_amount} HP!")

####################
# Player instance
####################

player = Player("Hero")
player.add_to_inventory(Weapon("Sword", 15))
player.add_to_inventory(Potion("Health Potion", 20))

####################
# Utility functions
####################

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()
