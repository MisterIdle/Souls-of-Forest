import os
import random

def main():
    print("Welcome to the game!")
    main_menu()

# Main menu

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

# Gameloop
show_map_flag = False

def gameloop():
    global show_map_flag
    clear_screen()
    print("=== Game Loop ===")
    
    print("1. Toggle Map")
    print("2. Inventory")
    print("Player position: ", player.getpos())

    if show_map_flag:
        show_map()

    print("Move: n/z (north), s/s (south), e/d (east), w/q (west) or exit")
    choice = input("Enter choice: ")

    if choice == "1":
        show_map_flag = True
    elif choice == "2":
        player.show_inventory()
        item_choice = input("Choose item number to use or press enter to return: ")
        if item_choice.isdigit():
            player.use_item(int(item_choice))
    elif choice in ["n", "s", "e", "w", "z", "d", "q"]:
        player.move(choice)
    elif choice == "exit":
        main_menu()
    else:
        print("Invalid choice. Please try again.")

    gameloop()

# Map

data_map = [
    ["#", "#", "#", "#", "#", "#", "#"],
    ["#", ".", ".", ".", ".", "E", "#"],
    ["#", ".", "#", ".", ".", ".", "#"],
    ["#", ".", ".", ".", "#", ".", "#"],
    ["#", "#", "#", "#", "#", "#", "#"]
]

def show_map():
    map_copy = [row[:] for row in data_map]
    
    px, py = player.getpos()
    
    if 0 <= py < len(map_copy) and 0 <= px < len(map_copy[0]):
        map_copy[py][px] = "@"

    for row in map_copy:
        print(" ".join(row))

# Entity

class Entity:
    def __init__(self, name):
        self.name = name
        self.hp = 100
        self.attack = 10
        self.defense = 5
        self.x = 1
        self.y = 1
        self.inventory = {}

    def getpos(self):
        return self.x, self.y

    def add_to_inventory(self, item):
        if item.name in self.inventory:
            self.inventory[item.name]["quantity"] += 1
        else:
            self.inventory[item.name] = {"item": item, "quantity": 1}

    def show_inventory(self):
        print("Inventory:")
        for i, (item_name, item_info) in enumerate(self.inventory.items(), start=1):
            quantity = item_info["quantity"]
            print(f"{i}. {item_name} x{quantity}")

    def use_item(self, item_number):
        if 1 <= item_number <= len(self.inventory):
            item_name = list(self.inventory.keys())[item_number - 1]
            item_info = self.inventory[item_name]
            item = item_info["item"]
            item.use(self)
            if item_info["quantity"] > 1:
                self.inventory[item_name]["quantity"] -= 1
            else:
                del self.inventory[item_name]
        else:
            print("Invalid item number.")

# Player

class Player(Entity):
    def __init__(self, name):
        super().__init__(name)

    def move(self, direction):
        if (direction == "n" or direction == "z") and self.y > 0:
            self.y -= 1
        elif direction == "s" and self.y < len(data_map) - 1:
            self.y += 1
        elif (direction == "e" or direction == "d") and self.x < len(data_map[0]) - 1:
            self.x += 1
        elif (direction == "w" or direction == "q") and self.x > 0:
            self.x -= 1

# Enemies

class Enemy(Entity):
    def __init__(self, name):
        super().__init__(name)
    
class Slime(Enemy):
    def __init__(self):
        super().__init__("Slime")
        self.hp = 50
        self.attack = 5
        self.defense = 2

class Goblin(Enemy):
    def __init__(self):
        super().__init__("Goblin")
        self.hp = 70
        self.attack = 7
        self.defense = 3

class Dragon(Enemy):
    def __init__(self):
        super().__init__("Dragon")
        self.hp = 100
        self.attack = 15
        self.defense = 10

# Set enemy in map

data_map[2][2] = "S"
data_map[3][3] = "G"
data_map[1][5] = "D"

# Item system

class Item:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class Potion(Item):
    def __init__(self, name, effect_type, effect_amount):
        super().__init__(name)
        self.effect_type = effect_type
        self.effect_amount = effect_amount

    def use(self, target):
        print(f"{target.name} uses {self.name}!")
        if self.effect_type == "heal":
            target.hp += self.effect_amount
            print(f"{target.name}'s HP increased by {self.effect_amount}.")
        elif self.effect_type == "defense":
            target.defense += self.effect_amount
            print(f"{target.name}'s Defense increased by {self.effect_amount}.")

class Weapon(Item):
    def __init__(self, name, attack_power, crit_chance):
        super().__init__(name)
        self.attack_power = attack_power
        self.crit_chance = crit_chance

    def attack(self):
        crit = random.random() < self.crit_chance
        damage = self.attack_power * 2 if crit else self.attack_power
        print(f"{self.name} {'critically ' if crit else ''}hits for {damage} damage!")
        return damage

# Add items to player's inventory

player = Player("Player")
player.add_to_inventory(Potion("Health Potion", "heal", 30))
player.add_to_inventory(Potion("Health Potion", "heal", 30))
player.add_to_inventory(Potion("Defense Potion", "defense", 10))
player.add_to_inventory(Weapon("Sword", 10, 0.2))
player.add_to_inventory(Weapon("Dagger", 6, 0.5))

# Utils

def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

if __name__ == "__main__":
    main()
