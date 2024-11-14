import os
import json
import time
import msvcrt as inp

# Main variables for the game
max_width = 50
skip_animation = False

# Load JSON data from file
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

# Load game data
def load_game_data():
    entities_data = load_json("data/entities.json")
    lootable_data = load_json("data/lootable.json")
    map_data = load_json("data/map.json")
    tiles_data = load_json("data/tiles.json")
    items_data = load_json("data/items.json")
    shop_data = load_json("data/shop.json")
    dialogue_data = load_json("data/dialogues.json")

    if None in [entities_data, lootable_data, map_data, tiles_data, items_data]:
        print("Error: Some data files could not be loaded correctly.")
        return None, None, None, None, None

    return entities_data, lootable_data, map_data, tiles_data, items_data, shop_data, dialogue_data

entities_data, lootable_data, map_data, tiles_data, items_data, shop_data, dialogue_data = load_game_data()

# Clear the screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Load ASCII image from file
def load_ascii_image(filename, centered=False):
    try:
        with open(f"images/{filename}.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                if centered:
                    print(line.strip().center(max_width))
                else:
                    print(line, end='')
            print()

    except FileNotFoundError:
        print(f"Image '{filename}.txt' not found.")
    except UnicodeDecodeError:
        print(f"Error decoding the file '{filename}.txt'. Ensure the file is in UTF-8 encoding.")

# Print dialogue with character and line
def print_dialogue(character, line, speed=0.05):
    global skip_animation
    clear_screen()
    load_ascii_image(character.lower(), centered=True)

    text = dialogue_data[character.capitalize()][line]
    full_text_displayed = False

    for letter in text:
        if inp.kbhit() and inp.getch() == b'\r':
            clear_screen()
            load_ascii_image(character.lower(), centered=True)
            print(text)
            full_text_displayed = True
            break
        print(letter, end='', flush=True)
        time.sleep(speed)
    
    if not full_text_displayed:
        print()
    
    wait()
    clear_screen()


# Wait for player to press Enter
def wait():
    input("Press Enter to continue...")

# Print a line of '='
def line():
    print("=" * max_width)

# Print a centered text
def print_centered(text):
    print(f"{text}".center(max_width))

# Print a left-aligned text
def print_right(text):
    print(f"{text}".rjust(max_width))

# Print a right-aligned text
def print_both(text, text2):
    half_width = max_width // 2
    left_text = f"    {text[:half_width]}".ljust(half_width)
    right_text = f"{text2[:half_width]}".rjust(half_width)
    print(left_text + right_text)

# Print a left-aligned text
def wait():
    input("Press Enter to continue...")