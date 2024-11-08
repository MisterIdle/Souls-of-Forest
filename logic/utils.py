import os
import json

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

def exit_game():
    print("Exiting game...")
    input("Press any key to continue...")
    quit()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')