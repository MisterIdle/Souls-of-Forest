import logic.map as m
import logic.utils as u
import logic.entities as e

game_map = None
player = None

def main_menu():
    u.clear_screen()
    print("=== Main Menu ===")
    print("[1] Start game")
    print("[2] Continue")
    print("[X] Exit")
    choice = input("Enter choice: ")
    if choice == "1":
        new_game()
    elif choice.lower() == "x":
        print("Exiting game")
    else:
        print("Invalid choice")
        main_menu()

def new_game():
    u.clear_screen()
    print("Starting new game")
    global game_map, player
    
    m.Map.load_all_maps()
    game_map = m.Map.get_map('Tutorial')
    if game_map is None:
        print("Error: 'forest' map could not be loaded.")
        return
    
    print("Map loaded")

    player = e.Player(u.entities_data["player"])
    player.name = input("Enter player name: ")
    
    input("Press Enter to start game")
    game_loop()


def game_loop():
    u.clear_screen()
    print("=== Game ===")
    player.print_stats()
    
    game_map.display(player.position)
    
    print("[Z/Q/S/D] Move or [N]orth/[W]est/[E]ast/[S]outh")
    print("[B] Bag")
    print("[P] Pick up item")
    print("[X] Exit")

    choice = input("Enter choice: ").strip().lower()

    if choice in ["z", "q", "s", "d", "n", "w", "e"]:
        player.move(choice, game_map)
        game_loop()
    elif choice == "b":
        print("Opening bag")
        player.use_inventory()
        game_loop()
    elif choice == "p":
        player.pick_up_item()
        game_loop()
    elif choice == "x":
        print("Exiting game")
    else:
        print("Invalid choice")
        game_loop()

