import logic.map as m
import logic.utils as utils
import logic.entities as e
import logic.save as s
import msvcrt as inp
import time as t

# Main variables for the game
game_map = None
player = None
explored_maps = {}
save = s.Save()
use_input = False

# Main menu
def main_menu():
    utils.clear_screen()
    utils.load_ascii_image("logo")
    print("=== Main Menu ===")
    print("[1] Start game")
    print("[2] Continue")
    print("[3] Delete save")
    print("[X] Exit")
    choice = input("Enter choice: ")
    
    if choice == "1":
        new_game()
    elif choice == "2":
        continue_game()
    elif choice == "3":
        delete_save()
    elif choice.lower() == "x":
        exit_game()
    else:
        print("Invalid choice")
        main_menu()

# New game
def new_game():
    utils.clear_screen()
    print("Starting new game")
    global game_map, player, explored_maps
    
    load_maps()
    game_map = m.Map.get_map('Tutorial')
    if game_map is None:
        print(f"Error: Map {game_map} is not loaded.")
        return
    
    print("Map loaded")
    load_all()

    utils.clear_screen()
    ambience()
    set_player_name()
    intro()
    game_loop()

# Load maps
def load_maps():
    m.Map.load_all_maps()

# Load all
def load_all():
    global player
    player = e.Player(utils.entities_data["player"])
    global explored_maps
    explored_maps["Tutorial"] = game_map

# Ambience message
def ambience():
    print("Hello, type in Spotify or other")
    print("    'Medieval ambience' ")
    print("Good luck on your adventure ;)")
    utils.wait()
    utils.clear_screen()

# Set player name
def set_player_name():
    player.name = input("Enter player name: ")
    if not player.name:
        utils.clear_screen()
        print("Please enter a valid name")
        set_player_name()

    utils.clear_screen()
    t.sleep(1)

# Intro
def intro():
    utils.print_dialogue("Narrator", "intro")
    utils.print_dialogue("Narrator", "intro2")
    utils.print_dialogue("Narrator", "intro3")
    utils.print_dialogue("Narrator", "intro4")
    utils.print_dialogue("Narrator", "intro5")
    utils.print_dialogue("Narrator", "intro6")
    utils.print_dialogue("Narrator", "intro7")
    utils.print_dialogue("Narrator", "intro8")
    utils.print_dialogue("Narrator", "intro9")

# Continue game
def continue_game():
    print("Loading game")
    list_saves()
    save_number = input("Enter the number of the save you want to load or [Back]: ").strip().lower()

    if save_number.isdigit():
        save_files = save.get_save_files()
        if 1 <= int(save_number) <= len(save_files):
            save_name = save_files[int(save_number) - 1]
            confirmed = input(f"Are you sure you want to load {save_name}? [Y/N] ").strip().lower()
            if confirmed in ["y", "yes"]:
                loaded_maps, loaded_player = save.load_game(save_name)
                if loaded_maps and loaded_player:
                    global explored_maps, game_map, player
                    explored_maps = loaded_maps
                    player = loaded_player
                    game_map = explored_maps[player.current_map]
                    game_loop()
                else:
                    print("Error loading game")
                    utils.wait()
                    main_menu()
            elif confirmed in ["n", "no"]:
                main_menu()
            else:
                print("Invalid choice, please choose a valid save number.")
                continue_game()
        else:
            print("Invalid choice, please choose a valid save number.")
            continue_game()
    elif save_number in ["b", "back"]:
        main_menu()
    else:
        print("Invalid choice")
        continue_game()

# Delete save
def delete_save():
    print("Deleting save")
    list_saves()
    save_number = input("Enter the number of the save you want to delete or [Back]: ").strip().lower()

    if save_number.isdigit():
        save_files = save.get_save_files()
        if 1 <= int(save_number) <= len(save_files):
            confirm = input(f"Are you sure you want to delete {save_files[int(save_number) - 1]}? [Y/N] ").strip().lower()
            if confirm in ["y", "yes"]:
                save.delete_save(save_files[int(save_number) - 1])
                utils.wait()
                main_menu()
            elif confirm in ["n", "no"]:
                main_menu()
        else:
            print("Invalid choice, please choose a valid save number.")
            delete_save()
    elif save_number in ["b", "back"]:
        main_menu()
    else:
        print("Invalid choice")
        delete_save()

# List saves
def list_saves():
    print("=== Available Saves ===")
    saves = save.get_save_files()
    if saves:
        for idx, save_file in enumerate(saves, 1):
            print(f"{idx}. {save_file}")
    else:
        print("No saved games found.")

# Exit game
def exit_game():
    print("Exiting game")

# Game loop
def game_loop():
    global explored_maps
    utils.clear_screen()
    display_game_map()
    display_player_stats()
    display_controls()

    choice = inp.getch().decode('utf-8').lower()

    if choice in ["z", "q", "s", "d", "n", "w", "e", "s"]:
        player.move(choice, game_map)
        game_loop()
    elif choice in ["\x26", "\x25", "\x28", "\x27"]:
        console_mode()
    elif choice in ["b", "bag", "inventory", "i", "items", "inv"]:
        open_bag()
    elif choice in ["p", "pick", "pickup"]:
        pickup_items()
    elif choice in ["o", "options"]:
        open_options()
    # Ctrl+C
    elif choice == '\x03':
        handle_exit()
    else:
        print("Invalid choice")
        game_loop()

# Display player stats
def display_player_stats():
    utils.line()
    utils.print_centered("=== Player Stats ===")
    utils.line()
    player.print_stats()
    player.xp_to_next_level()
    utils.line()
    print()

# Display game map
def display_game_map():
    print()
    player.current_map = game_map.map_name
    utils.load_ascii_image(game_map.get_tile_name(player.position), centered=True)
    print()
    game_map.map_compass(player.position)
    game_map.show_items_on_tile(player.position)

# Display controls
def display_controls():
    print("Move [Z/Q/S/D] [N/W/E/S]")
    print("[bag] [pick] [option]")

# Console mode
def console_mode():
    print("You are in the console")
    utils.wait()

# Open bag
def open_bag():
    print("Opening bag")
    player.use_inventory()
    game_loop()

# Pickup items
def pickup_items():
    player.see_items_on_tile()
    game_loop()

# Open options
def open_options():
    print("Options")
    print("[save] [exit]")
    choice = input("Enter choice: ").strip().lower()

    if choice in ["x", "exit"]:
        confirm_exit()
    elif choice in ["s", "save"]:
        save_game()
    else:
        print("Invalid choice")
        game_loop()

# Confirm exit
def confirm_exit():
    confirm = input("Are you sure you want to exit? [Y/N] ").strip().lower()
    if confirm in ["y", "yes"]:
        print("Exiting game")
        save_confirmation = input("Do you want to save the game? [Y/N] ").strip().lower()
        if save_confirmation in ["y", "yes"]:
            save_game()
        elif save_confirmation in ["n", "no"]:
            pass
        else:
            print("Invalid choice")
    elif confirm in ["n", "no"]:
        game_loop()
    else:
        print("Invalid choice")
        game_loop()

# Save game
def save_game():
    save_name = input("Enter save name: ").strip()
    print(f"Saving game as {save_name}")
    save.save_game(explored_maps, player, save_name)
    print("Game saved")
    utils.wait()
    game_loop()

# Handle exit
def handle_exit():
    confirm = input("Are you sure you want to exit? [Y/N] ").strip().lower()
    if confirm in ["y", "yes"]:
        print("Exiting game")
        save.save_game(explored_maps, player)
    elif confirm in ["n", "no"]:
        game_loop()
    else:
        print("Invalid choice")
        game_loop()
