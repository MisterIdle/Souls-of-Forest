import os
import random

def main():
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
        player.move(move.lower())
    
    gameloop()

# Map
data_map = [
    ["#", "#", "#", "#", "#", "#", "#"],
    ["#", "F", ".", ".", ".", "E", "#"],
    ["#", ".", "#", ".", ".", ".", "#"],
    ["#", ".", ".", ".", "#", ".", "#"],
    ["#", "#", "#", "#", "#", "#", "#"]
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
        print(f"{self.name}'s Inventory:")
        for i, (item_name, item_info) in enumerate(self.inventory.items(), 1):
            print(f"{i}. {item_name} ({item_info['quantity']})")

    def show_stats(self):
        print(f"{self.name}'s Stats:")
        print(f"HP: {self.hp}")
        print(f"Attack: {self.attack}")
        print(f"Defense: {self.defense}")

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

# Set enemies in map
data_map[2][2] = "S"
data_map[3][3] = "G"
data_map[1][5] = "D"

# Item system
class Item:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

    def __str__(self):
        return self.name

class Potion(Item):
    def __init__(self, name, effect_amount, weight):
        super().__init__(name, weight)
        self.effect_amount = effect_amount

    def use(self, target):
        print(f"{target.name} uses {self.name}!")
        self.apply_effect(target)

    def apply_effect(self, target):
        pass

class HealthPotion(Potion):
    def __init__(self, effect_amount):
        super().__init__("Health Potion", effect_amount, 0.5)

    def apply_effect(self, target):
        target.hp += self.effect_amount
        print(f"{target.name}'s HP increased by {self.effect_amount}.")

class DefensePotion(Potion):
    def __init__(self, effect_amount):
        super().__init__("Defense Potion", effect_amount, 0.5)

    def apply_effect(self, target):
        target.defense += self.effect_amount
        print(f"{target.name}'s Defense increased by {self.effect_amount}.")

class Weapon(Item):
    def __init__(self, name, attack_power, crit_chance, weight):
        super().__init__(name, weight)
        self.attack_power = attack_power
        self.crit_chance = crit_chance

    def attack(self):
        crit = random.random() < self.crit_chance
        damage = self.attack_power * 2 if crit else self.attack_power
        print(f"{self.name} {'critically ' if crit else ''}hits for {damage} damage!")
        return damage

# Add items to player's inventory
player = Player("Player")
player.add_to_inventory(HealthPotion(30))
player.add_to_inventory(HealthPotion(30))
player.add_to_inventory(DefensePotion(10))
player.add_to_inventory(Weapon("Sword", 10, 0.2, 1.36))  # 3 lbs = 1.36 kg
player.add_to_inventory(Weapon("Dagger", 6, 0.5, 0.68))  # 1.5 lbs = 0.68 kg

# Initialize the map
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

# Utils
def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

if __name__ == "__main__":
    main()
