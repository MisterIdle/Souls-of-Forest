import os
import json

def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format - {file_path}")
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
    return None

def load_game_data():
    entities_data = load_json("data/entities.json")
    lootable_data = load_json("data/lootable.json")
    map_data = load_json("data/map.json")
    tiles_data = load_json("data/tiles.json")
    items_data = load_json("data/items.json")

    if None in [entities_data, lootable_data, map_data, tiles_data, items_data]:
        print("Error: Some data files could not be loaded correctly.")
        return None, None, None, None, None

    return entities_data, lootable_data, map_data, tiles_data, items_data

entities_data, lootable_data, map_data, tiles_data, items_data = load_game_data()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
