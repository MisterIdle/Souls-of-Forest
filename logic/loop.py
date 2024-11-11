import logic.map as m
import logic.utils as u
import logic.entities as e
import logic.save as s

game_map = None
player = None
explored_maps = {}
save = s.Save()

def main_menu():
    global game_map, player, explored_maps
    u.clear_screen()
    print("=== Main Menu ===")
    print("[1] Start game")
    print("[2] Continue")
    print("[X] Exit")
    choice = input("Enter choice: ")
    if choice == "1":
        new_game()
    elif choice == "2":
        print("Loading game")
        explored_maps, player = save.load_game()
        if explored_maps is None or player is None:
            print("Error loading game")
            main_menu()
        game_loop()
    elif choice.lower() == "x":
        print("Exiting game")
    else:
        print("Invalid choice")
        main_menu()

def new_game():
    u.clear_screen()
    print("Starting new game")
    global game_map, player, explored_maps
    
    m.Map.load_all_maps()
    game_map = m.Map.get_map('Tutorial')
    if game_map is None:
        print(f"Error: Map {game_map} is not loaded.")
        return
    
    print("Map loaded")

    player = e.Player(u.entities_data["player"])
    player.name = input("Enter player name: ")
    
    explored_maps["Tutorial"] = game_map
    u.wait()
    game_loop()

def game_loop():
    global explored_maps
    u.clear_screen()
    print("=== Game ===")
    player.print_stats()
    player.xp_to_next_level()
    print()
    player.current_map = game_map.map_name
    
    game_map.map_display(player.position)
    game_map.map_compass(player.position)
    game_map.show_items_on_tile(player.position)
    
    print("Move [Z/Q/S/D] [N/W/E/S]")
    print("Pickup [P] | Bag [B] | Exit [X] | Save [S]")

    choice = input("> ").strip().lower()

    if choice in ["z", "q", "s", "d", "n", "w", "e"]:
        player.move(choice, game_map)
        game_loop()
    elif choice in ["b", "bag", "inventory", "i", "items", "inv"]:
        print("Opening bag")
        player.use_inventory()
        game_loop()
    elif choice in ["p", "pick", "pickup"]:
        player.see_items_on_tile()
        game_loop()
    elif choice in ["x", "exit", "quit"]:
        confirm = input("Are you sure you want to exit? [Y/N] ").strip().lower()
        if confirm in ["y", "yes"]:
            print("Exiting game")
            save.save_game(explored_maps, player)
        elif confirm in ["n", "no"]:
            game_loop()
        else:
            print("Invalid choice")
            game_loop()
    elif choice in ["s", "save"]:
        save.save_game(explored_maps, player)
        game_loop()
    else:
        print("Invalid choice")
        game_loop()
